import json
import http.client
import os.path
import mimetypes
import time
import ssl
import urllib.parse, urllib.request, urllib.error

"""
The functions in this file will make use of the ShareFile API v3 to show some of the basic
operations using GET, POST, PATCH, DELETE HTTP verbs. See api.sharefile.com for more information.

Requirements:
All required libraries should be part of most standard python installations.
Functions were converted from functions tested in python 2.7.1 for use with python 3.x

Authentication:
OAuth2 password grant is used for authentication. After the token is acquired it is sent an an
authorization header with subsequent API requests.

Exception / Error Checking:
For simplicity, exception handling has not been added.  Code should not be used in a production environment.
"""

def authenticate(hostname, client_id, client_secret, username, password):
    """ Authenticate via username/password. Returns json token object.

    Args:
    string hostname - hostname like "myaccount.sharefile.com"
    string client_id - OAuth2 client_id key
    string client_secret - OAuth2 client_secret key
    string username - my@user.name
    string password - my password """

    uri_path = '/oauth/token'

    headers = {'Content-Type':'application/x-www-form-urlencoded'}
    params = {'grant_type':'password', 'client_id':client_id, 'client_secret':client_secret,
                'username':username, 'password':password}

    #set the ssl context to not verify SSL certificate
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    #set a global http object for the connection to be referred to by other functions
    global http
    http = http.client.HTTPSConnection(hostname,context=ctx)
    http.request('POST', uri_path, urllib.parse.urlencode(params), headers=headers)
    response = http.getresponse()

    print(response.status, response.reason)
    token = None
    if response.status == 200:
        token = json.loads(str(response.read(),'utf-8'))
        print('Received token info', token)

    http.close()
    return token

def get_authorization_header(token):
    return {'Authorization':'Bearer %s'%(token['access_token'])}

def get_hostname(token):
    return '%s.sf-api.com'%(token['subdomain'])

def get_root(token, get_children=False):
    """ Get the root level Item for the provided user. To retrieve Children the $expand=Children
    parameter can be added.

    Args:
    dict json token acquired from authenticate function
    boolean get_children - retrieve Children Items if True, default is False"""

    uri_path = '/sf/v3/Items(allshared)'
    if get_children:
        uri_path = '%s?$expand=Children'%(uri_path)
    print('GET %s%s'%(get_hostname(token), uri_path))

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()

    print(response.status, response.reason)
    items = json.loads(str(response.read(),'utf-8'))
    print(items['Id'], items['CreationDate'], items['Name'])
    if 'Children' in items:
        children = items['Children']
        for child in children:
            print(child['Id'], items['CreationDate'], child['Name'])

def get_item_by_id(token, item_id):
    """ Get a single Item by Id.

    Args:
    dict json token acquired from authenticate function
    string item_id - an item id """

    uri_path = '/sf/v3/Items(%s)'%(item_id)
    print('GET %s%s'%(get_hostname(token), uri_path))

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()

    print(response.status, response.reason)
    items = json.loads(str(response.read(),'utf-8'))
    print(items['Id'], items['CreationDate'], items['Name'])
    return {'Id':items['Id'],'CreationDate':items['CreationDate'],'Name':items['Name']}

def get_folder_with_query_parameters(token, item_id):
    """ Get a folder using some of the common query parameters that are available. This will
    add the expand, select parameters. The following are used:

    expand=Children to get any Children of the folder
    select=Id,Name,Children/Id,Children/Name,Children/CreationDate to get the Id, Name of the folder
    and the Id, Name, CreationDate of any Children

    Args:
    dict json token acquired from authenticate function
    string item_id - a folder id """

    uri_path = '/sf/v3/Items(%s)?$expand=Children&$select=Id,Name,Children/Id,Children/Name,Children/CreationDate'%(item_id)
    print('GET %s%s'%(get_hostname(token), uri_path))

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()

    print(response.status, uuuresponse.reason)
    items = json.loads(str(response.read(),'utf-8'))
    print(items['Id'], items['Name'])
    if 'Children' in items:
        children = items['Children']
        for child in children:
            print(child['Id'], child['CreationDate'], child['Name'])

    http.close()

def create_folder(token, parent_id, name, description):
    """ Create a new folder in the given parent folder.

    Args:
    dict json token acquired from authenticate function
    string parent_id - the parent folder in which to create the new folder
    string name - the folder name
    string description - the folder description """

    uri_path = '/sf/v3/Items(%s)/Folder'%(parent_id)
    print('POST %s%s'%(get_hostname(token), uri_path))
    folder = {'Name':name, 'Description':description}
    headers = get_authorization_header(token)
    headers['Content-Type'] = 'application/json'

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('POST', uri_path, json.dumps(folder), headers=headers)
    response = http.getresponse()

    print(response.status, response.reason)
    new_folder = json.loads(str(response.read(),'utf-8'))
    print('Created Folder %s'%(new_folder['Id']))

    http.close()

def update_item(token, item_id, name, description):
    """ Update the name and description of an Item.

    Args:
    dict json token acquired from authenticate function
    string item_id - the id of the item to update
    string name - the item name
    string description - the item description """


    uri_path = '/sf/v3/Items(%s)'%(item_id)
    print('PATCH %s%s'%(get_hostname(token), uri_path))
    folder = {'Name':name, 'Description':description}
    headers = get_authorization_header(token)
    headers['Content-type'] = 'application/json'

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('PATCH', uri_path, json.dumps(folder), headers=headers)
    response = http.getresponse()

    print(response.status, response.reason)
    http.close()

def delete_item(token, item_id):
    """ Delete an Item by Id.

    Args:
    dict json token acquired from authenticate function
    string item_id - the id of the item to delete """

    uri_path = '/sf/v3/Items(%s)'%(item_id)
    print('DELETE %s%s'%(get_hostname(token), uri_path))

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('DELETE', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()

    print(response.status, response.reason)
    http.close()

def download_item(token, item_id, local_path):
    """ Downloads a single Item. If downloading a folder the local_path name should end in .zip.

    Args:
    dict json token acquired from authenticate function
    string item_id - the id of the item to download
    string local_path - where to download the item to, like "c:\\path\\to\\the.file" """

    uri_path = '/sf/v3/Items(%s)/Download'%(item_id)
    print('GET %s%s'%(get_hostname(token), uri_path))

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()
    location = response.getheader('location')
    redirect = None
    if location:
        redirect_uri = urllib.parse.urlparse(location)
        redirect = http.client.HTTPSConnection(redirect_uri.netloc)
        redirect.request('GET', '%s?%s'%(redirect_uri.path, redirect_uri.query))
        response = redirect.getresponse()

    with open(local_path, 'wb') as target:
        b = response.read(1024*8)
        while b:
            target.write(b)
            b = response.read(1024*8)

    print(response.status, response.reason)
    http.close()
    if redirect:
        redirect.close()

def upload_file(token, folder_id, local_path):
    """ Uploads a File using the Standard upload method with a multipart/form mime encoded POST.

    Args:
    dict json token acquired from authenticate function
    string folder_id - where to upload the file
    string local_path - the full path of the file to upload, like "c:\\path\\to\\file.name" """

    uri_path = '/sf/v3/Items(%s)/Upload'%(folder_id)
    print('GET %s%s'%(get_hostname(token), uri_path))

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))

    response = http.getresponse()
    upload_config = json.loads(str(response.read(),'utf-8'))
    if 'ChunkUri' in upload_config:
        upload_response = multipart_form_post_upload(upload_config['ChunkUri'], local_path)
        print(upload_response.status, upload_response.reason)
    else:
        print('No Upload URL received')

def multipart_form_post_upload(url, filepath):
    """ Does a multipart form post upload of a file to a url.

    Args:
    string url - the url to upload file to
    string filepath - the complete file path of the file to upload like, "c:\path\to\the.file

    Returns:
    the http response """

    import http.client

    newline = '\r\n'
    filename = os.path.basename(filepath)
    data = []
    headers = {}
    boundary = '----------%d' % int(time.time())
    headers['content-type'] = 'multipart/form-data; boundary=%s' % boundary
    data.append('--%s' % boundary)
    data.append('Content-Disposition: form-data; name="%s"; filename="%s"' % ('File1', filename))
    data.append('Content-Type: %s' % get_content_type(filename))
    data.append('')
    data.append(open(filepath, 'r').read())
    data.append('--%s--' % boundary)
    data.append('')

    print(data)

    data_str = newline.join(data)
    headers['content-length'] = len(data_str)

    uri = urllib.parse.urlparse(url)
    http = http.client.HTTPSConnection(uri.netloc)
    http.putrequest('POST', '%s?%s'%(uri.path, uri.query))
    for hdr_name, hdr_value in list(headers.items()):
        http.putheader(hdr_name, hdr_value)
    http.endheaders()
    http.send(data_str.encode('utf-8'))
    return http.getresponse()

def get_content_type(filename):
    return mimetypes.guess_type(filename)[0] or 'application/octet-stream'

def get_clients(token):
    """ Get the Client users in the Account.

    Args:
    dict json token acquired from authenticate function """

    uri_path = '/sf/v3/Accounts/GetClients'
    print('GET %s%s'%(get_hostname(token), uri_path))

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('GET', uri_path, headers=get_authorization_header(token))
    response = http.getresponse()

    print(response.status, response.reason)
    feed = json.loads(str(response.read(),'utf-8'))
    if 'value' in feed:
        for client in feed['value']:
            print(client['Id'], client['Email'])

def create_client(token, email, firstname, lastname, company,
                    clientpassword, canresetpassword, canviewmysettings):
    """ Create a Client user in the Account.

    Args:
    dict json token acquired from authenticate function
    string email - email address of the new user
    string firstname - firsty name of the new user
    string lastname - last name of the new user
    string company - company of the new user
    string clientpassword - password of the new user
    boolean canresetpassword - user preference to allow user to reset password
    boolean canviewmysettings - user preference to all user to view 'My Settings' """

    uri_path = '/sf/v3/Users'
    print('POST %s%s'%(get_hostname(token), uri_path))
    client = {'Email':email, 'FirstName':firstname, 'LastName':lastname, 'Company':company,
                'Password':clientpassword, 'Preferences':{'CanResetPassword':canresetpassword, 'CanViewMySettings':canviewmysettings}}
    headers = get_authorization_header(token)
    headers['Content-type'] = 'application/json'

    #global http
    #http = http.client.HTTPSConnection(get_hostname(token))
    http.request('POST', uri_path, json.dumps(client), headers=headers)
    response = http.getresponse()

    print(response.status, response.reason)
    new_client = json.loads(str(response.read(),'utf-8'))
    print('Created Client %s'%(new_client['Id']))

    http.close()

if __name__ == '__main__':
    hostname = "Hostname"
    username = "Username"
    password = "Password"
    client_id = 'Client_ID'
    client_secret = 'Client_Secret'

    token = authenticate(hostname, client_id, client_secret, username, password)
    if token:
        get_root(token, password)