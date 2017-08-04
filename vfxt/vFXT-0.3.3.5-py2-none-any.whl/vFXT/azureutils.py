#
# Utilities for making REST calls to the Azure cloud infrastructure.
__version__='0.1.1'

import datetime
import time
import hmac
import hashlib
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()
import requests
from requests.auth import AuthBase
from requests.exceptions import HTTPError
import functools
import threading
import logging
import random

log = logging.getLogger(__name__)

class AzureUtilsServiceException(Exception): pass
class AzureUtilsConfigurationException(Exception): pass

# cached oauth2 bearer tokens and subscription
CORE_RESOURCE='https://management.core.windows.net/'
GRAPH_RESOURCE='https://graph.windows.net/'

# the tenant is the tenant ID from "azure account list"
# the subscription is the subscription ID from "azure account list"
# the client_id is the application ID of the principal (not the application object ID)
# the secret is the password you used to create the principal
def getOAuthInfo(subscription_id,tenant,client_id,client_secret,force=False,session=None,resource=CORE_RESOURCE, retries=3):
    '''Return headers used for oauth authentication, suitable for use with the "requests" package'''

    if force or not oauth_tokens.get(resource):
        endpoint = 'https://login.microsoftonline.com/%s/oauth2/token'%tenant
        payload = {
            'grant_type': 'client_credentials',
            'client_id': client_id,
            'client_secret': client_secret,
            'resource': resource
        }
        if session:
            response = request_retry(retries, session.post, endpoint, data=payload).json()
        else:
            response = request_retry(retries, requests.post, endpoint, data=payload).json()
        if 'error' in response:
            raise AzureUtilsServiceException(response['error']+": "+response.get('error_description'))
        # store more of the response for expiry purposes
        oauth_tokens = {'access_token': response['access_token'],
                                  'expires_in':   response['expires_in'],
                                  'not_before':   response['not_before'],
                                  'expires_on':   response['expires_on'],
                                  'headers':      { 'Authorization': 'bearer {}'.format(response['access_token']) }
        }
    return oauth_tokens

# fetch the dictionary of storage keys
def _fetchStorageKeys(session, oauth_tokens, subscription_id, retries=3):
    headers = {
        'Authorization': 'bearer %s'%oauth_tokens['access_token']
    }

    if not session:
        session = requests.Session()

    response = request_retry(retries, session.get, 'https://management.azure.com/subscriptions/%s/resourceGroups?api-version=2015-01-01'%subscription_id,headers=headers)
    if response.status_code != 200:
        raise AzureUtilsServiceException("list resource groups failed: %d: %s"%(response.status_code,response.content))

    keys = {}
    for rg in response.json()['value']:
        response = request_retry(retries, session.get, 'https://management.azure.com/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Storage/storageAccounts?api-version=2015-06-15'%(subscription_id,rg['name']), headers=headers)
        if response.status_code != 200:
            raise AzureUtilsServiceException("list storage accounts for %s failed: %d: %s"%(rg['name'],response.status_code,response.content))
        for acct in response.json()['value']:
            # listkeys needs to be a POST with no body.   Go figure.
            response = request_retry(retries, session.post, 'https://management.azure.com/subscriptions/%s/resourceGroups/%s/providers/Microsoft.Storage/storageAccounts/%s/listKeys?api-version=2015-06-15'%(subscription_id,rg['name'],acct['name']), headers=headers)
            if response.status_code != 200:
                raise AzureUtilsServiceException("list keys for %s failed: %d: %s"%(acct['name'],response.status_code,response.content))
            keys[ (rg['name'].lower(),acct['name'].lower()) ] = response.json()['key1'].decode('base64')
    return keys

# a "requests" Auth class that does Azure Storage authentication
# See https://msdn.microsoft.com/en-us/library/azure/dd179428.aspx
class AzureStorageAuth(AuthBase):
    '''Class that does Azure Storage authentication.   Pass as the auth=
       parameter to 'requests' request APIs.
       This class supports API version 2009-09-19 and later.'''

    # the order of these matters
    StandardHdrs = ['Content-Encoding', 'Content-Language', 'Content-Length',
                   'Content-MD5', 'Content-Type', 'Date', 'If-Modified-Since',
                   'If-Match', 'If-None-Match', 'If-Unmodified-Since', 'Range']

    def __init__(self, account, key):
        self.key = key
        self.account = account

    def __call__(self, req):
        if 'x-ms-version' not in req.headers:
            req.headers['x-ms-version'] = '2015-02-21'
        req.headers['x-ms-date'] = datetime.datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S GMT")

        sig = self.calcSignature(req)
        req.headers['Authorization'] = 'SharedKey %s:%s'%(self.account,sig.encode('base64').strip())
        return req

    def calcSignature(self, req):
        stringToSign = req.method.upper() + '\n'

        # the standard headers are added in order
        for h in self.StandardHdrs:
            val = req.headers.get(h)

            # we override date with x-ms-date
            if h == 'Date':
                val = ''

            # empty reqs use 0 or '' for content-length depending on version
            if h == 'Content-Length':
                vers = req.headers['x-ms-version'].split('-')
                vers = datetime.date(int(vers[0]),int(vers[1]),int(vers[2]))
                if vers >= datetime.date(2015,02,21):
                    if val == '0': val = ''
                else:
                    if not val: val = '0'

            if val is None:
                val = ''
            stringToSign += val + '\n'

        # canonicalize remaining headers
        hdrs = []
        for h in req.headers:
            h = str(h).lower()
            if h.startswith('x-ms-'):
                hdrs.append( (h,req.headers.get(h,'')) )
        hdrs.sort()
        for i in hdrs:
            val = ' '.join(i[1].strip().split())   # crush all whitespace to single spaces
            stringToSign += '%s:%s\n'%(i[0],val)

        # canonicalize "resource"
        uri = req.url.split('?')
        query = ''
        if len(uri) > 1:
            query = uri[1]
        uri = '/'.join(uri[0].split('/')[3:])   # uri is part after https://host/
        stringToSign += '/%s/%s\n'%(self.account,uri)
        if query:
            queries = []
            for q in query.split('&'):
                (param, val) = q.split('=',1)
                queries.append( (param.lower(), val) )
            queries.sort()
            for q in queries:
                # TODO: url the param and val
                # TODO: handle duplicate params
                stringToSign += '%s:%s\n'%( q[0], q[1] )

        # the stringToSign shouldn't have a trailing '\n'
        stringToSign = stringToSign[:-1]
        log.debug('Auth: string to sign: "%s"',stringToSign)
        return hmac.new(self.key, msg=stringToSign, digestmod=hashlib.sha256).digest()

# XXX GAH, i know this is terrible... for now it makes it easier to read the blob xml response
def xmltodict(tree,is_root=True):
    import copy
    if is_root:
        return {tree.tag : xmltodict(tree, False)}
    d=copy.copy(tree.attrib)
    children = tree.findall("./*")
    if not children:
        return tree.text
    for x in children:
        tag = x.tag
        if tag not in d:
            d[tag]=[]
        d[tag].append(xmltodict(x,False))
    for k in d.keys():
        if len(d[k]) == 1:
            d[k] = d[k][0] # flatten
    return d
# formatting callbacks
def extract_containers(response, api, options):
    import xml.etree.ElementTree
    xml_str = response.text
    tree = xml.etree.ElementTree.fromstring(xml_str)
    root = tree.findall('./Containers')[0]
    containers = xmltodict(root)['Containers']
    if not containers:
        return []
    containers = containers['Container']
    # always needs to be a list, in case there is only one container
    if not isinstance(containers, list):
        containers = [containers]
    return containers

# This is a python "generator" that knows the Microsoft continuation protocol
def extract_blobs(response, api, options):
    import xml.etree.ElementTree
    while True:
        xml_str = response.text
        tree = xml.etree.ElementTree.fromstring(xml_str)
        root = tree.find('Blobs')
        if root is not None:
            for b in root.iter('Blob'):
                yield xmltodict(b)['Blob']
        nextMarker = tree.find('NextMarker')
        if nextMarker is None or nextMarker.text is None:
            return

        # redo the call, adding/replacing the marker= tag in the URL, and replace response.
        # TODO: find and use the session (if any)?
        req = response.request
        x = req.url.find('&marker=')
        if x < 0:
            req.url += '&marker=%s'%nextMarker.text
        else:
            url = req.url[:x] + '&marker=%s'%nextMarker.text
            y = req.url[x+len('&marker='):].find('&')
            if y > 0:
                url += req.url[x+len('&marker=')+y:]
            req.url = url
        response = api._request(req.method, req.url, auth_type='storage', response_type='stream', **options)
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise AzureUtilsServiceException(e.response.content)
        except:
            raise

def extract_snapshots(response, api, options):
    for b in extract_blobs(response, api, options):
        if not 'Snapshot' in b:
            continue
        yield b

def backoff(counter, max_backoff=30):
    return min(max_backoff, (2**counter) + (random.randint(0, 1000) / 1000.0))

def request_retry(allowed_errors, func, *args, **kwargs):
    response = None
    errors = 0
    while errors < allowed_errors:
        response = func(*args, **kwargs)
        if response.status_code in (409, 429, 503, 509):
            time.sleep(backoff(errors))
            errors += 1
            continue
        break
    return response

#
# API builder helper class.   Consumers don't instantiate this directly.
class _ApiBuilder(object):
    '''A class that simplifies making REST calls to the Azure virtual machine APIs'''

    def __init__(self, args, api):
        self.template = args[0]
        self.operations = args[1]
        self.api = api

    def __getattr__(self, name):
        if name in self.operations:
            return functools.partial(self._compose, self.operations[name])
        raise AttributeError(name)

    def _compose(self, operation, **args):
        ''' Compose a URL from an operation and a template.
            A template is a list of segment descriptors:
                ( name, 'template' )
            where name is either None, and the template has no params,
            or the name of a parameter that is interpolated into the template
            if it was in the 'required' list or supplied as a literal.  The
            resulting URL is the concatanation of all the segments.
            An operation is a tuple:
                ( HTML_OP, [ 'required_param', ... ], [ 'literal_param': 'value' ] )
            We throw an exception if one of the required_params is missing.
        '''
        url = ''
        for segment in self.template:
            if segment[0] is None:
                url += segment[1]
            elif segment[0] in operation[1] or segment[0] in args:
                # segment[0] is required if in operation[1], otherwise optional
                val = args.get(segment[0], None)
                if not val:
                    val = getattr(self.api, segment[0], None)
                if not val:
                    if segment[0] in operation[1]:
                        raise AzureUtilsConfigurationException("Must supply value for %s"%segment[0])
                else:
                    url += segment[1].format(val)
            elif len(operation) > 2 and segment[0] in operation[2]:
                val = operation[2].get(segment[0], None)
                if val:
                    url += segment[1].format(val)
                else:
                    url += segment[1]

        # XXX operation should be a dict
        auth_type = operation[3]
        response_type    = operation[4]
        # handle this ourself rather than expecting the caller to put it all together
        return self._request(operation[0], url, auth_type=auth_type, response_type=response_type, **args)

    def _request(self, method, url, auth_type='none', response_type=None, **options):
        '''Perform a request
            method_name (str): method to call (GET, POST, etc)
            url (string): URL to request
            auth_type: 'none', 'oauth': inject our OAUTH headers, 'storage': use StorageAuth
            response_type (str or function): json|xml|callback

            retry (int, optional): number of times to try, defaults 1

            As a special case, if we're in json mode and the top level dictionary
            contains just a 'value' key (and optionally a 'nextLink' key), we follow
            Microsoft's list return protocol and return an iterator to the values.
        '''
        log.debug('_request options: {}'.format(options))
        retries = int(options.get('retry', 3))

        headers = {}
        auth = None
        if auth_type == 'oauth':
            headers = self.api.gen_oauth_headers()
        elif auth_type == 'oauth_graph':
            headers = self.api.gen_oauth_headers(GRAPH_RESOURCE)
        elif auth_type == 'storage':
            auth    = self.api.gen_storage_auth(options)
        header_opts = options.get('headers', None)
        if header_opts:
            headers.update(header_opts)

        log.debug("{} {}".format(method, url))
        args = {}
        for k in ('data', 'json'):
            if k in options:
                args[k] = options[k]
        if self.api.proxy_uri:
            args['proxies'] = {
                'https': self.api.proxy_uri,
                'http': self.api.proxy_uri,
            }
        if self.api.timeout:
            args['timeout'] = self.api.timeout
        response = request_retry(retries, self.api.session().request, method, url, headers=headers, auth=auth, stream=(response_type=='stream'), **args)

        # look for a server errror messsage
        if response.status_code == 400:
            try:
                resp = response.json()    # throws if no resp or not json
                if 'error' in resp:
                    if 'message' in resp['error']:
                        raise AzureUtilsServiceException('400 Client Error: Bad Request: {}'.format(resp['error']['message']))
            except AzureUtilsServiceException:
                raise    # don't catch the exception we're raising!
            except:
                pass
        # otherwise look for an HTTP error
        try:
            response.raise_for_status()
        except HTTPError as e:
            msg = e
            try:
                e_json = e.response.json()
                msg = '{}: {}'.format(e_json['error']['code'], e_json['error']['message'])
            except: pass
            raise AzureUtilsServiceException(msg)
        except:
            raise

        try:
            if isinstance(response_type, basestring):
                if response_type == 'json':
                    retval = response.json()
                    listProto = True
                    for k in retval:
                        if k not in ( 'value', 'nextLink' ):
                            listProto = False
                            break
                    if listProto:
                        return self._listProtoHelper(response, retval, headers, options)
                    return retval
                if response_type == 'xml':
                    return response.text
                if response_type == 'raw':
                    return response.content
                if response_type == 'stream':
                    return response
                if response_type == 'headers':
                    return response.headers
            else:
                # or try a callback (these can be generators that make further calls)
                return response_type(response, self, options)
        except ValueError:
            pass                  # this usually means nothing was returned
        except Exception as e:
            log.debug("Failed trying to handle custom formatter for response: {}".format(e))
            raise AzureUtilsConfigurationException("Failed trying to handle custom formatter for response: {}".format(e))
        return response

    # generator that handles Microsoft's "list protocol"
    def _listProtoHelper(self, response, retval, headers, options):
        for r in retval['value']:
            yield r
        nextLink = None
        if 'nextLink' in retval:
            nextLink = retval['nextLink']
        if not nextLink:
            return

        retries = int(options.get('retry', 3))
        # get the next batch of items, using nextLink for the URL
        req = response.request

        log.debug("{} {}".format(req.method, nextLink))
        response = request_retry(retries, self.api.session().request, req.method, nextLink, headers=headers)
        try:
            response.raise_for_status()
        except HTTPError as e:
            raise AzureUtilsServiceException(e.response.content)
        except:
            raise
        retval = response.json()

#
# A class that encapsulates a lot of the goop required to make Azure REST calls.
# In particular, it includes a URL builder.
class AzureApi(object):
    '''A class that simplifies making REST calls to the Azure cloud APIs

        # Minimal
        api = AzureApi(client_id='', client_secret='', tenant='')
        # Full
        api = AzureApi(
                    subscription='',
                    client_id='',
                    client_secret='',
                    tenant='',
                    resource_group='',
                    storage_account='',
                    proxy_uri='',
                    timeout=10
        )

        Global operations:
            api.listTenants()
            api.listSubscriptions()
            api.listResources()
            api.listResourceGroups()
            api.listLocations()

        VM operations:
            api.virtualmachines.create(name='', json={})
            api.virtualmachines.deallocate(name='')
            api.virtualmachines.delete(name='')
            api.virtualmachines.get(name='')
            api.virtualmachines.generalize(name='', ...)
            api.virtualmachines.instanceView(name='')
            api.virtualmachines.list()
            api.virtualmachines.restart(name='')
            api.virtualmachines.start(name='')
            api.virtualmachines.stop(name='')
            api.virtualmachines.getUsage(location='')

        Availability sets:
            api.availabilitysets.create(name='')
            api.availabilitysets.delete(name='')
            api.availabilitysets.get(name='')
            api.availabilitysets.list()

        Locations:
            api.locations.listVmSizes(location='')
            api.locations.getOperation(location='', name='')

        Networks:
            api.networks.list()
            api.networks.listRouteTables()
            api.networks.getRouteTable(name='')
            api.networks.listRoutes(table='')
            api.networks.createRoute(table='', name='', json={})
            api.networks.deleteRoute(table='', name='')
            api.networks.getNIC(name='')
            api.networks.createNIC(name='', json={})
            api.networks.deleteNIC(name='')
            api.networks.listNICs()
            api.networks.getUsage()
            api.networks.getNetwork(network='')
            api.networks.getSubnet(network='', subnet='')
            api.networks.createPublicAddress(name='', json={})
            api.networks.deletePublicAddress(name='', json={})
            api.networks.getPublicAddress(name='')

        Storage Accounts:
            api.storageaccounts.list()
            api.storageaccounts.get(name='')
            api.storageaccounts.getUsage()

        RBAC:
            api.rbac.listRoles()
            api.rbac.createRole(id='', json={})
            api.rbac.getRole(id='')
            api.rbac.deleteRole(id='')
            api.rbac.listAssignments()
            api.rbac.createAssignment(id='', json={})
            api.rbac.getAssignment(id='')
            api.rbac.deleteAssigment(id='')

        Blob:
            api.blob.listContainers(storage_account='')
            api.blob.list(storage_account='', container='')
            api.blob.createContainer(storage_account, container='')
            api.blob.create(storage_account='', container='', blob='', ...)
            api.blob.copy(storage_account='', container='', blob='', headers={'x-ms-copy-source':''}
            api.blob.delete(storage_account='', container='', blob='')
            api.blob.deleteContainer(storage_account='', container='')
            api.blob.get(storage_account='', container='', blob='')
            api.blob.getProperties(storage_account='', container='', blob='')
            api.blob.getStream(storage_account='', container='', blob='')
            api.blob.snapshot(storage_account='', container='', blob='')
            api.blob.listSnapshots(storage_account='')
            api.blob.deleteSnapshot(storage_account='', container='', blob='', snapshot='')

            api.blob.create(container='azutil-test', blob='testblob',  headers={'x-ms-blob-type':'PageBlob', 'x-ms-blob-content-length': '512'})
            api.blob.create(container='image-builder', blob='woodwardj-builder', headers={'x-ms-blob-type':'BlockBlob'}, data='')

        Active Directory:
            api.activedirectory.listUsers()
            api.activedirectory.getApplicadtion(id='')
            api.activedirectory.listApplications()
            api.activedirectory.createApplication(id='', json={})
            api.activedirectory.deleteApplication(id='')

            api.ad.createApplication(id='test', json={'availableToOtherTenants':False, 'displayName':'test', 'passwordCredentials':[{'keyId':str(uuid.uuid4()), 'value':'secret'}]})
    '''

    # see _ApiBuilder.compose for the structure of an "Operation" and "Template"
    GlobalTemplate = [
        (None, 'https://management.azure.com'),
        ('subscription', '/subscriptions/{}'),
        ('resource_group', '/resourceGroups/{}'),
        ('_suffix', '/{}'),
        (None, '?api-version=2015-11-01'),
        ('_options', '{}'),
    ]
    GlobalOperations = {
        'listTenants':  ('GET',[],{'_suffix': 'tenants'},
                               'oauth', 'json'),
        'listSubscriptions':  ('GET',[],{'_suffix': 'subscriptions'},
                               'oauth', 'json'),
        'listResources': ('GET',['subscription'],{'_suffix': 'resources'},
                               'oauth', 'json'),
        'listResourceGroups': ('GET',['subscription'],{'_suffix': 'resourceGroups'},
                               'oauth', 'json'),
        'listLocations':  ('GET',['subscription'],{'_suffix': 'locations'},
                               'oauth', 'json'),
    }

    VMTemplate = [
        (None, 'https://management.azure.com'),
        ('subscription', '/subscriptions/{}'),
        ('resource_group', '/resourceGroups/{}'),
        (None, '/providers/Microsoft.Compute'),
        ('name', '/virtualmachines/{}'),
        ('location', '/locations/{}'),
        ('_suffix', '/{}'),
        (None, '?api-version=2015-06-15'),
        ('_options', '{}'),
    ]
    VMOperations = {
        'create': ('PUT',['subscription','resource_group','name'], {},
                    'oauth', 'json'),
        'deallocate': ('POST',['subscription','resource_group','name'],{'_suffix': 'deallocate'},
                    'oauth', 'json'),
        'delete': ('DELETE',['subscription','resource_group','name'],{},
                   'oauth', 'json'),
        'get': ('GET',['subscription','resource_group','name'],{},
                'oauth', 'json'),
        'generalize': ('POST',['subscription','resource_group','name'],{'_suffix': 'generalize'},
                       'oauth', 'json'),
        'instanceView': ('GET',['subscription','resource_group','name'],{'_suffix':'instanceView'},
                         'oauth', 'json'),
        'list': ('GET',['subscription','resource_group'],{'_suffix':'virtualmachines'},
                 'oauth', 'json'),
        'restart': ('POST',['subscription','resource_group','name'],{'_suffix': 'restart'},
                    'oauth', 'json'),
        'start': ('POST',['subscription','resource_group','name'],{'_suffix': 'start'},
                  'oauth', 'json'),
        'stop': ('POST',['subscription','resource_group','name'],{'_suffix': 'powerOff'},
                 'oauth', 'json'),
        'getUsage': ('GET', ['subscription','location'],{'_suffix': 'usages'},
                               'oauth', 'json'),
    }

    ASetTemplate = [
        (None, 'https://management.azure.com'),
        ('subscription', '/subscriptions/{}'),
        ('resource_group', '/resourceGroups/{}'),
        (None, '/providers/Microsoft.Compute/availabilitySets'),
        ('name', '/{}'),
        (None, '?api-version=2015-05-01-preview'),
        ('_options', '{}'),
    ]
    ASetOperations = {
        'create': ('PUT',['subscription','resource_group','name'], {},
                    'oauth', 'json'),
        'delete': ('DELETE',['subscription','resource_group','name'], {},
                    'oauth', 'json'),
        'get': ('GET',['subscription','resource_group','name'], {},
                    'oauth', 'json'),
        'list': ('GET',['subscription','resource_group'], {},
                    'oauth', 'json'),
    }

    LocTemplate = [
        (None, 'https://management.azure.com'),
        ('subscription', '/subscriptions/{}'),
        ('resource_group', '/resourceGroups/{}'),
        (None, '/providers'),
        ('location', '/Microsoft.Compute/locations/{}'),
        ('_suffix', '/{}'),
        ('name', '/{}'),
        (None, '?api-version=2015-05-01-preview'),
        ('_options', '{}'),
    ]
    LocOperations = {
        'listVmSizes': ('GET',['subscription','location'],{'_suffix': 'vmSizes'},
                        'oauth', 'json'),
        'getOperation': ('GET',['subscription','location','name'],{'_suffix': 'operations'},
                        'oauth', 'json'),
    }

    NetworkTemplate = [
        (None, 'https://management.azure.com'),
        ('subscription', '/subscriptions/{}'),
        ('resource_group', '/resourceGroups/{}'),
        (None, '/providers/Microsoft.Network'),
        ('location', '/locations/{}'),
        ('table', '/routeTables/{}'),
        ('network', '/virtualNetworks/{}'),
        ('subnet', '/subnets/{}'),
        ('_subprovider', '/{}'),
        ('name', '/{}'),
        ('_suffix', '/{}'),
        (None, '?api-version=2016-03-30'),
        ('_options', '{}'),
    ]
    NetworkOperations = {
        'list': ('GET',['subscription'],    # may optionally supply resource_group
                                {'_subprovider':'virtualnetworks'},'oauth', 'json'),
        'listRouteTables': ('GET',['subscription','resource_group'],
                                {'_subprovider':'routeTables'},'oauth','json'),
        'getRouteTable': ('GET',['subscription','resource_group','name'],
                                {'_subprovider':'routeTables'},'oauth','json'),
        'listRoutes':('GET',['subscription','resource_group','table'],
                                {'_subprovider':'routes'},'oauth','json'),
        'createRoute':('PUT',['subscription','resource_group','table','name'],
                                {'_subprovider':'routes'},'oauth','json'),
        'deleteRoute':('DELETE',['subscription','resource_group','table','name'],
                                {'_subprovider':'routes'},'oauth','json'),
        'getNIC':    ('GET',['subscription','resource_group','name'],
                                {'_subprovider':'networkInterfaces'},'oauth','json'),
        'createNIC': ('PUT',['subscription','resource_group','name'],
                                {'_subprovider':'networkInterfaces'},'oauth','json'),
        'deleteNIC': ('DELETE',['subscription','resource_group','name'],
                                {'_subprovider':'networkInterfaces'},'oauth','json'),
        'listNICs':  ('GET',['subscription'],
                                {'_subprovider':'networkInterfaces'},'oauth', 'json'),
        'getUsage': ('GET', ['subscription','location'],{'_suffix': 'usages'},
                               'oauth', 'json'),
        'getNetwork': ('GET',['subscription', 'resource_group', 'network'],
                                {},'oauth', 'json'),
        'getSubnet': ('GET',['subscription', 'resource_group', 'network', 'subnet'],
                                {},'oauth', 'json'),
        'createPublicAddress': ('PUT', ['subscription', 'resource_group', 'name'],
                                {'_subprovider': 'publicIPAddresses'}, 'oauth', 'json'),
        'deletePublicAddress': ('DELETE', ['subscription', 'resource_group', 'name'],
                                {'_subprovider':'publicIPAddresses'},'oauth', 'json'),
        'getPublicAddress': ('GET', ['subscription', 'resource_group', 'name'],
                                {'_subprovider':'publicIPAddresses'},'oauth', 'json'),
    }

    StorageAcctTemplate = [
        (None, 'https://management.azure.com'),
        ('subscription', '/subscriptions/{}'),
        ('resource_group', '/resourceGroups/{}'),
        (None, '/providers/Microsoft.Storage'),
        ('name', '/storageAccounts/{}'),
        ('_suffix', '/{}'),
        (None, '?api-version=2015-06-15')
    ]
    StorageAcctOperations = {
        'list': ('GET',['subscription'],{'_suffix':'storageAccounts'}, # you can supply resource_group if desired
                 'oauth', 'json'),
        'get': ('GET',['subscription', 'resource_group', 'name'],{},
                 'oauth', 'json'),
        'getUsage': ('GET',['subscription'],{'_suffix':'usages'},
                 'oauth', 'json'),
    }

    RBACTemplate = [
        (None, 'https://management.azure.com'),
        ('subscription', '/subscriptions/{}'),
        ('resource_group', '/resourceGroups/{}'),
        (None, '/providers/Microsoft.Authorization'),
        ('_suffix', '/{}'),
        ('id', '/{}'),
        (None, '?api-version=2015-07-01')
    ]
    RBACOperations = {
        'listRoles': ('GET',['subscription'],
                      {'_suffix':'roleDefinitions'},
                      'oauth', 'json'),
        'createRole':('PUT',['subscription','resource_group','id'],
                      {'_suffix':'roleDefinitions'},
                      'oauth', 'json'),
        'getRole':   ('GET',['subscription','resource_group','id'],
                      {'_suffix':'roleDefinitions'},
                      'oauth', 'json'),
        'deleteRole':('DELETE',['subscription','resource_group','id'],
                      {'_suffix':'roleDefinitions'},
                      'oauth', 'json'),
        'listAssignments': ('GET',['subscription','resource_group'],
                      {'_suffix':'roleAssignments'},
                      'oauth', 'json'),
        'createAssignment':('PUT',['subscription','resource_group','id'],
                      {'_suffix':'roleAssignments'},
                      'oauth', 'json'),
        'getAssignment':   ('GET',['subscription','resource_group','id'],
                      {'_suffix':'roleAssignments'},
                      'oauth', 'json'),
        'deleteAssignment':('DELETE',['subscription','resource_group','id'],
                      {'_suffix':'roleAssignments'},
                      'oauth', 'json'),
    }

    BlobTemplate = [
        (None, 'https://'),
        ('storage_account', '{}.blob.core.windows.net'),
        ('container', '/{}'),
        ('blob', '/{}'),
        ('_restype', '?restype={}'),
        ('_comp', '?comp={}'),
        ('snapshot', '?snapshot={}'),
        ('containerlist', '?restype=container&comp=list'),
        ('snapshotlist', '?restype=container&comp=list&include=snapshots'),
    ]
    BlobOperations = {
        'listContainers': ('GET', ['storage_account'], {'_comp': 'list'},
                            'storage', extract_containers),
        'list_containers': ('GET', ['storage_account'], {'_comp': 'list'},
                            'storage', extract_containers),            # deprecated
        'list': ('GET', ['storage_account', 'container'], {'containerlist':True},
                       'storage', extract_blobs),
        'createContainer': ('PUT', ['storage_account', 'container'], {'_restype': 'container'},
                             'storage', 'xml'),
        'create_container': ('PUT', ['storage_account', 'container'], {'_restype': 'container'},
                             'storage', 'xml'),            # deprecated
        'create': ('PUT', ['storage_account', 'container', 'blob'], {},
                        'storage', 'xml'),
        'copy': ('PUT', ['storage_account', 'container', 'blob'], {},
                        'storage', 'headers'),
        'delete': ('DELETE', ['storage_account', 'container', 'blob'], {},
                        'storage', 'xml'),
        'deleteContainer': ('DELETE', ['storage_account', 'container'], {'_restype': 'container'},
                             'storage', 'xml'),
        'get': ('GET', ['storage_account', 'container', 'blob'], {},
                        'storage', 'raw'),
        'getProperties': ('HEAD', ['storage_account', 'container', 'blob'], {},
                        'storage', 'headers'),
        'getStream': ('GET', ['storage_account', 'container', 'blob'], {},
                        'storage', 'stream'),
        'snapshot': ('PUT', ['storage_account', 'container', 'blob'], {'_comp':'snapshot'},
                        'storage', 'headers'),
        'listSnapshots': ('GET', ['storage_account'], {'snapshotlist':True},
                            'storage', extract_snapshots),
        'deleteSnapshot': ('DELETE', ['storage_account', 'container', 'blob', 'snapshot'], {},
                        'storage', 'xml'),
    }

    ADTemplate = [
        (None, 'https://graph.windows.net'),
        ('tenant', '/{}'),
        ('_restype', '/{}'),
        ('id', '/{}'),
        (None, '?api-version=1.6'),
    ]
    ADOperations = {
        'listUsers': ('GET', ['tenant'], {'_restype': 'users'},
                      'oauth_graph', 'json'),
        'getApplication': ('GET', ['tenant', 'id'], {'_restype': 'applications'},
                      'oauth_graph', 'json'),
        'listApplications': ('GET', ['tenant'], {'_restype': 'applications'},
                      'oauth_graph', 'json'),
        'createApplication': ('POST', ['tenant', 'id'], {'_restype': 'applications'},
                      'oauth_graph', 'json'),
        'deleteApplication': ('DELETE', ['tenant', 'id'], {'_restype': 'applications'},
                      'oauth_graph', 'json'),
    }

    AzureAPIs = {
        '_global': (GlobalTemplate, GlobalOperations),
        'vm': (VMTemplate, VMOperations),
        'virtualmachines': (VMTemplate, VMOperations),
        'availabilitysets': (ASetTemplate, ASetOperations),
        'locations': (LocTemplate, LocOperations),
        'networks': (NetworkTemplate, NetworkOperations),
        'storageaccounts': (StorageAcctTemplate, StorageAcctOperations),
        'rbac': (RBACTemplate, RBACOperations),
        'blob': (BlobTemplate, BlobOperations),
        'ad': (ADTemplate, ADOperations),
        'activedirectory': (ADTemplate, ADOperations),
    }

    def __init__(self, subscription=None, resource_group=None,
                 client_id=None, client_secret=None, tenant=None,
                 storage_account=None, session=None, proxy_uri=None, timeout=None):
        # Lets store all of the credential information here
        self.subscription    = subscription
        self.resource_group  = resource_group
        self.client_id       = client_id
        self.client_secret   = client_secret
        self.tenant          = tenant
        self.storage_account = storage_account
        self.proxy_uri       = proxy_uri
        self.timeout         = timeout

        self.oauth_headers = {}
        self.storage_auth = {}
        self.storage_keys = {}

        self.local = threading.local() # https://github.com/kennethreitz/requests/issues/2766
        self.local.session = session

    def set(self, **args):
        for a in args:
            if not a in ('subscription','resource_group','tenant'):
                raise ValueError(a)
            setattr(self,a,args[a])

    def session(self):
        if not getattr(self.local,'session',None):
            self.local.session = requests.Session()
        return self.local.session

    def __getattr__(self, name):
        '''Provide URL building support along the lines of x.vm.get(name='armada-2')
        '''
        if name in self.AzureAPIs:
            return _ApiBuilder(self.AzureAPIs[name],self)
        elif name in self.GlobalOperations:
            return _ApiBuilder(self.AzureAPIs['_global'],self).__getattr__(name)

        raise AttributeError(name)

    def gen_oauth_headers(self,resource=CORE_RESOURCE):
        # somewhat simple cache for now
        try:
            if int(self.oauth_headers[resource]['expires_on']) < int(time.time())+60:
                log.debug("Expiring OAuth cache")
                del self.oauth_headers[resource]
                # might as well expire storage auth as well since we use gen_oauth_headers for the side effect
                self.storage_auth = {}
                # and the session for that matter... otherwise we get a long timeout for the existing connection
                del self.local.session
        except: pass

        if not resource in self.oauth_headers:
            log.debug("generating oauth headers for %s",resource)
            # any reason not to pass the session here?
            self.oauth_headers[resource] = getOAuthInfo(self.subscription, self.tenant, self.client_id, self.client_secret, force=True, session=self.session(), resource=resource)

        return self.oauth_headers[resource]['headers']

    def gen_storage_auth(self, args):
        rg = args['resource_group'] if 'resource_group' in args else self.resource_group
        account = args['storage_account']  if 'storage_account' in args else self.storage_account

        rg = rg.lower()
        account = account.lower()
        account_key_pair = ( rg, account )

        if not self.storage_keys or account_key_pair not in self.storage_keys:
            self.storage_keys = _fetchStorageKeys(session=self.session(), oauth_tokens=self.oauth_headers[CORE_RESOURCE], subscription_id=self.subscription)

        if account_key_pair  not in self.storage_keys:
            raise AzureUtilsServiceException("AzureStorageAuth: unknown storage account.")

        # simple cache for now
        if not account in self.storage_auth:
            log.debug("generating storage auth for %s",account)
            key = self.storage_keys[ (rg, account) ]
            self.storage_auth[account] = AzureStorageAuth(account, key)
        return self.storage_auth[account]


########
# Unit test driver
def main():
    import pprint
    import os

    logging.basicConfig()
    log = logging.getLogger(__name__)
    log.setLevel(logging.DEBUG)

    resource_group='DanRG2'
    subscription_id='646cce9f-0a1c-4acb-be06-401056b03659'
    tenant='cabd3237-12a4-4a0b-8851-e728f17738a3'
    client_id='792ccfa0-5ac1-4ad7-8f25-5b3680998237'
    client_secret=os.getenv('SECRET')
    if not client_secret:
        raise AzureUtilsConfigurationException('must provide SECRET in the environment')
    storage_account='dnydicks2'

    a = AzureApi(
        subscription=subscription_id,
        resource_group=resource_group,
        tenant=tenant,
        client_id=client_id,
        client_secret=client_secret,
        storage_account=storage_account
    )

    resp = a.listResources(_options='&$top=10')   # test _listProtoHelper
    for r in resp:
        print r['id']

    print [ sz['name'] for sz in a.locations.listVmSizes(location='eastus') ]
    print [ vm['name'] for vm in a.vm.list() ]
    try:
        pprint.pprint( a.vm.get(name='armada-1') )
    except Exception as e:
        print e

    print [ (rg['name'], rg['location']) for rg in a.listResourceGroups() ]

    print a.blob.list_containers()
    pprint.pprint( a.blob.list(container='vhds'))

    try:
        pprint.pprint( a.blob.create_container(container='azutil-test'))
    except Exception as e: pass # probably already exists

    pprint.pprint( a.blob.create(container='azutil-test', blob='testblob',  headers={'x-ms-blob-type':'PageBlob', 'x-ms-blob-content-length': '512'}))

    print a.blob.get(container='dist', storage_account='dnydicks2', blob='newinstall.tar.gz.sig')

    # snapshot
    snapshot = a.blob.snapshot(container='azutil-test', blob='testblob')
    # get snapshot properties
    a.blob.getProperties(container='azutil-test', blob='testblob', snapshot=snapshot['x-ms-snapshot'])

    # copy_response = a.blob.copy(container='jason-test', blob='dest.vhd', headers={'x-ms-copy-source':'https://m1rg2731.blob.core.windows.net/vhds/jeff-ubu0201613164848.vhd'})
    # a.blob.getProperties(container='jason-test', blob='dest.vh', headers={'x-ms-copy-id':copy_response['x-ms-copy-id']})

    import code
    code.interact(local=locals())

if __name__ == '__main__':
    main()
