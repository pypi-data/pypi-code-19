#!/usr/bin/python

# Copyright (c) 2012 EMC Corporation
# All Rights Reserved
#
# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.


# import python system modules

import common
from common import SOSError
from virtualdatacenter import VirtualDatacenter
from virtualarray import VirtualArray
from storagepool import StoragePool
from storagesystem import StorageSystem
import json
from tenant import Tenant
import quota
import sys


class VirtualPool(object):

    '''
    The class definition for operations on 'Class of Service'.
    '''

    URI_VPOOL = "/{0}/vpools"
    URI_VPOOL_BY_VDC_ID = "/{0}/vpools?vdc-id={1}"
    URI_VPOOL_SHOW = URI_VPOOL + "/{1}"
    URI_VPOOL_STORAGEPOOL = URI_VPOOL_SHOW + "/storage-pools"
    URI_VPOOL_ACL = URI_VPOOL_SHOW + "/acl"
    URI_TENANT = '/tenants/{0}'
    URI_VPOOL_DEACTIVATE = URI_VPOOL_SHOW + '/deactivate'
    URI_VPOOL_REFRESH_POOLS = URI_VPOOL_SHOW + "/refresh-matched-pools"
    URI_VPOOL_ASSIGN_POOLS = URI_VPOOL_SHOW + "/assign-matched-pools"
    URI_VPOOL_SEARCH = URI_VPOOL + "/search?name={1}"

    PROTOCOL_TYPE_LIST = ['FC', 'iSCSI', 'NFS', 'CIFS']
    CONDITION_TYPE = ['true', 'false']
    
    RPO_UNITS = ['SECONDS', 'MINUTES', 'HOURS', 'WRITES',
                 'BYTES', 'KB', 'MB', 'GB', 'TB']
    
    ALREADY_EXISTS_STR = 'label {0} already exists'

    def __init__(self, ipAddr, port):
        '''
        Constructor: takes IP address and port of the ECS instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port

    def vpool_list_uris(self, type, vdcname=None):
        '''
        This function will give us the list of VPOOL uris
        separated by comma.
        '''
        vdcuri = None
        vdcrestapi = None
        if(vdcname != None):
            vdcrestapi = self.URI_VPOOL_BY_VDC_ID.format(type, vdcname)
        else:
            vdcrestapi = self.URI_VPOOL.format(type)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET", vdcrestapi, None)

        o = common.json_decode(s)
        return o['virtualpool']

    def vpool_list(self, type, vdcname=None):
        '''
        this function is wrapper to the vpool_list_uris
        to give the list of vpool uris.
        '''
        uris = self.vpool_list_uris(type, vdcname)
        return uris

    def vpool_show_uri(self, type, uri, xml=False):
        '''
        This function will take uri as input and returns with
        all parameters of VPOOL like lable, urn and type.
        parameters
            uri : unique resource identifier.
        return
            returns with object contain all details of VPOOL.
        '''
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            self.URI_VPOOL_SHOW.format(type, uri), None, None)

        o = common.json_decode(s)
        if(o['inactive']):
            return None

        if(xml is False):
            return o

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            self.URI_VPOOL_SHOW.format(type, uri), None, None, xml)
        return s

    def vpool_show(self, name, type, xml=False):
        '''
        This function is wrapper to  with vpool_show_uri.
        It will take vpool name as input and do query for uri,
        and displays the details of given vpool name.
        parameters
            name : Name of the VPOOL.
            type : Type of the VPOOL { 'file', 'block' or 'object'}
        return
            returns with object contain all details of VPOOL.
        '''
        uri = self.vpool_query(name, type)
        vpool = self.vpool_show_uri(type, uri, xml)
        return vpool

    def vpool_list_by_hrefs(self, hrefs):
        res = common.list_by_hrefs(self.__ipAddr, self.__port, hrefs)
        return res

    def vpool_get_tenant(self, type, vpooluri):
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            self.URI_VPOOL_ACL.format(type, vpooluri), None, None)
        o = common.json_decode(s)
        tenantids = []
        acls = common.get_node_value(o, "acl")
        for acl in acls:
            tenantids.append(acl['tenant'])

        return tenantids

    def vpool_get_tenant_name(self, tenanturi):
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            self.URI_TENANT.format(tenanturi), None, None)
        o = common.json_decode(s)
        return o['name']

    def vpool_allow_tenant(self, name, type, tenant):
        '''
        This function is allow given vpool to use by given tenant.
        It will take vpool name, tenant  as inputs and do query for uris.
        parameters
            name : Name of the VPOOL.
            type : Type of the VPOOL { 'file' or 'block' }
            tenant : Name of the tenant
        '''
        uri = self.vpool_query(name, type)
        tenant_obj = Tenant(self.__ipAddr, self.__port)
        tenanturi = tenant_obj.tenant_query(tenant)
        parms = {
            'add': [{
                'privilege': ['USE'],
                'tenant': tenanturi,
            }]
        }

        body = json.dumps(parms)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "PUT",
            self.URI_VPOOL_ACL.format(type, uri), body)
        return s

    def vpool_remove_tenant(self, name, type, tenant):
        '''
        This function is dis-allow given vpool to use by given tenant.
        It will take vpool name, tenant  as inputs and do query for uris.
        parameters
            name : Name of the VPOOL.
            type : Type of the VPOOL { 'file' or 'block' }
            tenant : Name of the tenant
        '''
        uri = self.vpool_query(name, type)
        tenant_obj = Tenant(self.__ipAddr, self.__port)
        tenanturi = tenant_obj.tenant_query(tenant)
        parms = {
            'remove': [{
                'privilege': ['USE'],
                'tenant': tenanturi,
            }]
        }

        body = json.dumps(parms)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "PUT",
            self.URI_VPOOL_ACL.format(type, uri), body)
        return s

    def vpool_getpools(self, name, type):
        '''
        This function will Returns list of computed id's for all
        storage pools matching with the VPOOL.
        This list of pools will be used to do create Volumes.
        parameters
             Name : Name of VPOOL.
             type : type of VPOOL.
        return
            Returns list of computed id's for all
            storage pools matching with the VPOOL.
        '''
        uri = self.vpool_query(name, type)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            self.URI_VPOOL_STORAGEPOOL.format(type, uri), None, None)

        o = common.json_decode(s)
        output = common.list_by_hrefs(self.__ipAddr, self.__port,
                                      common.get_node_value(o, "storage_pool"))
        return output

    def vpool_refreshpools(self, name, type):
        '''
        This method re-computes the matched pools for this VPOOL and
        returns this information.
        This list of pools will be used to do create Volumes.
        parameters
             Name : Name of VPOOL.
             type : type of VPOOL.
        '''
        uri = self.vpool_query(name, type)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            self.URI_VPOOL_REFRESH_POOLS.format(type, uri), None, None)

        o = common.json_decode(s)
        output = common.list_by_hrefs(self.__ipAddr, self.__port,
                                      common.get_node_value(o, "storage_pool"))
        return output

    def vpool_addpools(self, name, type, pools, serialno, devicetype):
        '''
        This method allows a user to update assigned matched pools.
        This list of pools will be used to do create Volumes.
        parameters
             Name : Name of VPOOL.
             type : type of VPOOL.
             pools: Storage pools to be added to VPOOL.
        '''
        poolidlist = []
        spobj = StoragePool(self.__ipAddr, self.__port)
        for pname in pools:
            (sid, pid) = spobj.storagepool_query(pname, None,
                                                 serialno, devicetype)
            poolidlist.append(pid)

        # Get the existing assigned pools, so that this call wont overwrite.
        uri = self.vpool_query(name, type)
        vpool = self.vpool_show_uri(type, uri)
        if(vpool and 'assigned_storage_pools' in vpool):
            for matpool in vpool['assigned_storage_pools']:
                poolidlist.append(matpool['id'])

        parms = {'assigned_pool_changes':
                 {'add': {
                     'storage_pool': poolidlist}}}

        body = json.dumps(parms)
        uri = self.vpool_query(name, type)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "PUT",
            self.URI_VPOOL_ASSIGN_POOLS.format(type, uri), body, None)

        o = common.json_decode(s)
        return o

    def vpool_removepools(self, name, type, pools, serialno, devicetype):
        '''
        This method allows a user to update assigned matched pools.
        This list of pools will be used to do create Volumes.
        parameters
             Name : Name of VPOOL.
             type : type of VPOOL.
             pools: Storage pools to be added to VPOOL.
        '''
        poolidlist = []
        spobj = StoragePool(self.__ipAddr, self.__port)

        for pname in pools:
            (sid, pid) = spobj.storagepool_query(pname, None,
                                                 serialno, devicetype)
            poolidlist.append(pid)

        parms = {'assigned_pool_changes':
                 {'remove': {
                     'storage_pool': poolidlist}}}

        body = json.dumps(parms)
        uri = self.vpool_query(name, type)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "PUT",
            self.URI_VPOOL_ASSIGN_POOLS.format(type, uri), body, None)

        o = common.json_decode(s)
        return o

    def get_protection_policy(self, params):
        '''
        This function will take protection policy parameters
        in the form of journalsize:remotecopymode:rpovalue:rpotype
        Type of RPO unit
      
        * @valid SECONDS = Seconds (time-based RPO)
        * @valid MINUTES = Minutes (time-based RPO)
        * @valid HOURS = Hours (time-based RPO)
        * @valid WRITES = Number of writes (transaction-based RPO)
        * @valid BYTES = Bytes (sized-based RPO)
        * @valid KB = Kilobytes (sized-based RPO)
        * @valid MB = Megabytes (sized-based RPO)
        * @valid GB = Gigabytes (sized-based RPO)
        * @valid TB = Terabytes (sized-based RPO)
    
        returns the array of entries for source policy.
        '''
        copyParam = []
        try:
            copyParam = params.split(":")
        except Exception as e:
            raise SOSError(SOSError.CMD_LINE_ERR,
                               " Please provide valid format " +
                               "journalsize:remotecopymode:rpovalue:rpotype ")
        copy = dict()
        if(not len(copyParam)):
            raise SOSError(SOSError.CMD_LINE_ERR,
                               " Please provide valid source policy ")
        copy['journal_size'] = copyParam[0]
        if(len(copyParam) > 1):
            copy['remote_copy_mode'] = copyParam[1]
        if(len(copyParam) > 2):
            copy['rpo_value'] = copyParam[2]
        if(len(copyParam) > 3):
            if ( copyParam[3].upper() not in VirtualPool.RPO_UNITS ):
                raise SOSError(SOSError.CMD_LINE_ERR,
                               " Please provide valid RPO type from " +
                               ",".join(VirtualPool.RPO_UNITS))
            copy['rpo_type'] = copyParam[3].upper()        
            
        return copy

    def get_protection_entries(self, type, params):
        '''
        This function will take type of protection and protection parameters
        in the form of varray:vpool:copypolicy.
        returns the array of entries for remote_copies.
        '''
        copies = params
        if not isinstance(params, list):
            copies = [params]
        copyEntries = []
        nh_obj = VirtualArray(self.__ipAddr, self.__port)
        varrays = []
        for copy in copies:
            copyParam = []
            try:
                copyParam = copy.split(":")
            except Exception as e:
                if(type == "ha"):
                    raise SOSError(SOSError.CMD_LINE_ERR,
                               " Please provide valid format " +
                               "hatype:varray:vpool ")
                else:
                    raise SOSError(SOSError.CMD_LINE_ERR,
                               " Please provide valid format " +
                               "varray:vpool:copypolicy ")
            copy = dict()
            if(not len(copyParam)):
                if(type == "ha"):
                    raise SOSError(SOSError.CMD_LINE_ERR,
                               " Please provide atleast ha type ")
                else:
                    raise SOSError(
                        SOSError.CMD_LINE_ERR,
                        "Please provide atleast varray for srdf/rp protection")
            if(type != "ha"):
                varray = nh_obj.varray_query(copyParam[0])
                if(varray in varrays):
                    raise SOSError(SOSError.CMD_LINE_ERR,
                               " Please provide different varrays in copies" )
                varrays.append(varray)    
                copy['varray'] = varray
                if(len(copyParam) > 1):
                    copy['vpool'] = self.vpool_query(copyParam[1], "block")
                if(len(copyParam) > 2):
                    if(type == "srdf"):
                        copy['remote_copy_mode'] = copyParam[2]
                    else:
                        copy['policy'] = {'journal_size': copyParam[2]}
                copyEntries.append(copy)
            else:
                copy['type'] = copyParam[0]
                haVarrayUri = None
                haVpoolUri = None
                if(len(copyParam) > 1):
                    haVarrayUri = nh_obj.varray_query(copyParam[1])
                if(len(copyParam) > 2):
                    haVpoolUri = self.vpool_query(copyParam[2], "block")
                useAsRecoverPointSource = False
                if(len(copyParam) > 3):
                    useAsRecoverPointSource = copyParam[3]
                copy['ha_varray_vpool'] = \
                    {'varray': haVarrayUri,
                     'vpool': haVpoolUri,
                     'useAsRecoverPointSource': useAsRecoverPointSource}
                copyEntries.append(copy)

        # In case of HA, contains single entry
        if(type == "ha"):
            return copyEntries[0]
        return copyEntries

    def vpool_create(self, name, description, type, protocols,
                     varrays, provisiontype, rp, rp_policy,
                     systemtype, raidlevel, fastpolicy, drivetype, expandable,
                     usematchedpools, max_snapshots, max_mirrors, vpoolmirror,
                     multivolconsistency, autotierpolicynames,
                     ha, minpaths,
                     maxpaths, pathsperinitiator, srdf, fastexpansion,
                     thinpreallocper):
        '''
        This is the function will create the VPOOL with given name and type.
        It will send REST API request to ECS instance.
        parameters:
            name : Name of the VPOOL.
            type : Type of the VPOOL { 'file', 'block' or 'object'}
            max_snapshots: max number of native snapshots
            max_mirrors: max number of native continuous copies
        return
            returns with VPOOL object with all details.
        '''
        parms = dict()
        if (name):
            parms['name'] = name
        if (description):
            parms['description'] = description
        if (protocols):
            parms['protocols'] = protocols

        if(provisiontype):
            pt = None
            if(provisiontype.upper() == 'THICK'):
                pt = 'Thick'
            elif (provisiontype.upper() == 'THIN'):
                pt = 'Thin'
            else:
                raise SOSError(
                    SOSError.SOS_FAILURE_ERR,
                    "VPOOL create error: Invalid provisiontype: " +
                    provisiontype)
            parms['provisioning_type'] = pt

        if(systemtype):
            parms['system_type'] = systemtype

        if(varrays):
            urilist = []
            nh_obj = VirtualArray(self.__ipAddr, self.__port)
            for varray in varrays:
                nhuri = nh_obj.varray_query(varray)
                urilist.append(nhuri)
            parms['varrays'] = urilist

        if(usematchedpools):
            if(usematchedpools.upper() == "TRUE"):
                parms['use_matched_pools'] = "true"
            else:
                parms['use_matched_pools'] = "false"

        if(type == 'file'):
           # max snapshot for file protection
            if(max_snapshots):
                vpool_protection_snapshots_param = dict()
                vpool_protection_snapshots_param[
                    'max_native_snapshots'] = max_snapshots

                file_vpool_protection_param = dict()
                file_vpool_protection_param[
                    'snapshots'] = vpool_protection_snapshots_param
                # file vpool params
                parms['protection'] = file_vpool_protection_param

            if(max_mirrors or rp or srdf):
                raise SOSError(
                    SOSError.CMD_LINE_ERR,
                    " Protection parameters('-max_mirrors'," +
                    "'-rp'or '-srdf') " +
                    "Invalid for file type vpool")
        else:
            # A path is an Initiator Target combination, Is applied as
            # a per Host limit
            if (maxpaths):
                parms['max_paths'] = maxpaths
            if (minpaths):
                parms['min_paths'] = minpaths
            if(pathsperinitiator is not None):
                parms['paths_per_initiator'] = pathsperinitiator
            if (thinpreallocper):
                parms['thin_volume_preallocation_percentage'] = thinpreallocper    

            if(raidlevel):
                if(systemtype is None):
                    raise SOSError(
                        SOSError.SOS_FAILURE_ERR,
                        "VPOOL create error: argument " +
                        "-systemtype/-st is required ")
                parms['raid_levels'] = raidlevel

            # fast policy type
            if(fastpolicy is not None):
                parms['auto_tiering_policy_name'] = fastpolicy

            if(drivetype):
                parms['drive_type'] = drivetype

                                # volume expansion is support
            if(expandable):
                parms['expandable'] = expandable
            
            if(fastexpansion):
                parms['fast_expansion'] = fastexpansion
                
            if(autotierpolicynames):
                parms['unique_auto_tier_policy_names'] = \
                    autotierpolicynames

            if (multivolconsistency):
                parms['multi_volume_consistency'] = multivolconsistency

            # highavailability
            if(ha):
                parms['high_availability'] = \
                    self.get_protection_entries("ha", ha)
            # protection
            if(max_mirrors or rp or
               max_snapshots or srdf):
                block_vpool_protection_param = dict()

                # vpool mirror protection
                if(max_mirrors):
                    vpool_protection_mirror_params = dict()
                    # for protection mirror it is mandatory
                    vpool_protection_mirror_params[
                        'max_native_continuous_copies'] = max_mirrors
                    if (vpoolmirror):  # it's an optional data
                        vpool_protection_mirror_params[
                            'protection_mirror_vpool'] = \
                            self.vpool_query(vpoolmirror, "block")
                    block_vpool_protection_param[
                        'continuous_copies'] = \
                        vpool_protection_mirror_params

                # rp protection
                if (rp):
                    vpool_protection_rp_params = dict()

                    # Journal size for source volume copy
                    if(rp_policy):
                        vpool_protection_rp_params['source_policy'] = \
                            self.get_protection_policy(rp_policy)

                    vpool_protection_rp_params['copies'] = \
                        self.get_protection_entries("rp", rp)
                    block_vpool_protection_param['recoverpoint'] = \
                        vpool_protection_rp_params

                # max snapshot for block
                if (max_snapshots):
                    # base class attribute
                    vpool_protection_snapshot_params = dict()
                    vpool_protection_snapshot_params[
                        'max_native_snapshots'] = max_snapshots
                    block_vpool_protection_param['snapshots'] = \
                        vpool_protection_snapshot_params
                # SRDF protection is the the remote replication for
                # VMAX. expecting the srdf parameter as
                # varray:vpool:copypolicy
                if(srdf):
                    cos_protection_srdf_params = dict()
                    cos_protection_srdf_params[
                        'remote_copy_settings'] = \
                        self.get_protection_entries("srdf", srdf)
                    block_vpool_protection_param['remote_copies'] = \
                        cos_protection_srdf_params
                # block protection
                parms['protection'] = block_vpool_protection_param

        body = json.dumps(parms)
        try:
            (s, h) = common.service_json_request(
                self.__ipAddr, self.__port, "POST",
                self.URI_VPOOL.format(type), body)
            o = common.json_decode(s)
            return o
        # Removed the duplicate name checking from CLi as API service 
        # validating the same.
        except SOSError as e:
            if(str(e.err_text).find(
                str(VirtualPool.ALREADY_EXISTS_STR.format(name))) != -1):
                raise SOSError(SOSError.ENTRY_ALREADY_EXISTS_ERR,
                           "VPOOL with name " + name +
                           " (" + type + ") " + "already exists")
            else:
                raise e
                

    def vpool_update(
            self, name, label, description, type, protocol_add,
            protocol_remove, varray_add, varray_remove, use_matched_pools,
            max_snapshots, max_mirrors, multivolconsistency, expandable,
            autotierpolicynames, ha,
            fastpolicy, minpaths, maxpaths, pathsperinitiator, srdfadd,
            srdfremove, rp_policy, add_rp,
            remove_rp, quota_enable, quota_capacity, fastexpansion,
            thinpreallocper):
        '''
        This is the function will update the VPOOL.
        It will send REST API request to ECS instance.
        parameters:
            name : Name of the VPOOL.
            label: new name of VPOOL
            type : Type of the VPOOL { 'file', 'block' or 'object'}
            desc : Description of VPOOL
            protocol_add : Protocols to be added
            protocol_remove : Protocols to be removed
            varray_add: varray to  be added
            varray_remove : varrays to be removed
            multipaths: No of multi paths
            max_snapshots: max number of native snapshots
            max_mirrors: max number of native continuous copies
        return
            returns with VPOOL object with all details.
        '''
        # check for existance of vpool.
        vpooluri = self.vpool_query(name, type)

        # update quota
        if(quota_enable is not None or quota_capacity is not None):
            from quota import Quota
            quota_obj = Quota(self.__ipAddr, self.__port)
            quota_obj.update(quota_enable, quota_capacity, type + "_vpool",
                             vpooluri)

        parms = dict()
        if (label):
            parms['name'] = label
        if (description):
            parms['description'] = description
        if (multivolconsistency):
            parms['multi_volume_consistency'] = multivolconsistency
        if (thinpreallocper):
            parms['thin_volume_preallocation_percentage'] = thinpreallocper        
        if (protocol_add):
            protocollist = []
            vpool = self.vpool_show_uri(type, vpooluri)
            if(vpool is not None):
                # get the existing protocol
                if('protocols' in vpool):
                    protocollist = vpool['protocols']

                for protocol in protocol_add:
                    if(not protocol in protocollist):
                        protocollist.append(protocol)
            parms['protocol_changes'] = {'add': {'protocol': protocollist}}

        if (protocol_remove):
            # check payload "protocols" attribute
            vpool = self.vpool_show_uri(type, vpooluri)
            if(vpool is not None):
                if('protocols' in vpool):
                    protocollist = vpool['protocols']
                # check deleted protocol exist in existing protocol list in
                # VirtualPool.
                for protocol in protocol_remove:
                    if(not protocol in protocollist):
                        raise SOSError(SOSError.SOS_FAILURE_ERR,
                                       "Invalid protocol (" +
                                       protocol + ") to remove: ")
            parms['protocol_changes'] = \
                {'remove': {'protocol': protocol_remove}}

        nhobj = VirtualArray(self.__ipAddr, self.__port)
        varrays = varray_add
        if(varrays is None):
            varrays = varray_remove
        nhurilist = []
        if(varrays is not None):
            for varray in varrays:
                nhurilist.append(nhobj.varray_query(varray))

        if (varray_add):
            parms['varray_changes'] = {'add': {'varrays': nhurilist}}

        if (varray_remove):
            parms['varray_changes'] = {'remove': {'varrays': nhurilist}}

        if(max_mirrors or max_snapshots or srdfadd or srdfremove or
           rp_policy or add_rp or remove_rp):
            vpool_protection_param = dict()
            if (max_snapshots):
                # base class attribute
                vpool_protection_snapshot_params = dict()
                vpool_protection_snapshot_params['max_native_snapshots'] = \
                    max_snapshots
                vpool_protection_param['snapshots'] = \
                    vpool_protection_snapshot_params

            if(max_mirrors):
                vpool_protection_mirror_params = dict()
                vpool_protection_mirror_params[
                    'max_native_continuous_copies'] = max_mirrors
                vpool_protection_param['continuous_copies'] = \
                    vpool_protection_mirror_params

            # SRDF protection is the the remote replication for VMAX.
            # expecting the srdf parameter as varray:vpool:copypolicy
            if(srdfadd or srdfremove):
                cos_protection_srdf_params = dict()
                if(srdfadd):
                    cos_protection_srdf_params[
                        'add_remote_copies_settings'] = \
                        self.get_protection_entries("srdf", srdfadd)
                if(srdfremove):
                    cos_protection_srdf_params[
                        'remove_remote_copies_settings'] = \
                        self.get_protection_entries("srdf", srdfremove)
                vpool_protection_param['remote_copies'] = \
                    cos_protection_srdf_params

            if(rp_policy or add_rp or remove_rp):
                vpool_protection_rp_params = dict()

                # Journal size for source volume copy
                if(rp_policy):
                    vpool_protection_rp_params['source_policy'] = \
                            self.get_protection_policy(rp_policy)
                if(add_rp):
                    vpool_protection_rp_params['add_copies'] = \
                        self.get_protection_entries("rp", add_rp)
                if(remove_rp):
                    vpool_protection_rp_params['remove_copies'] = \
                        self.get_protection_entries("rp", remove_rp)

                vpool_protection_param['recoverpoint'] = \
                    vpool_protection_rp_params

            parms['protection'] = vpool_protection_param

        if (use_matched_pools is not None):
            if(use_matched_pools == "true" or use_matched_pools == "True" or
               use_matched_pools == "TRUE"):
                parms['use_matched_pools'] = "true"
            else:
                parms['use_matched_pools'] = "false"

        if(expandable):
            vpool = self.vpool_show_uri(type, vpooluri)
            if(vpool['num_resources'] == 0):
                parms['expandable'] = expandable
            else:
                raise SOSError(SOSError.SOS_FAILURE_ERR,"Update virtual pool is not allowed if it has active resources")

                
        if(fastexpansion):
            parms['fast_expansion'] = fastexpansion

                            # highavailability
        if(ha):
            parms['high_availability'] = \
                self.get_protection_entries("ha", ha)

        if(fastpolicy):
            if(fastpolicy.lower() == "none"):
                parms['auto_tiering_policy_name'] = ""
            else:
                parms['auto_tiering_policy_name'] = fastpolicy

        if(autotierpolicynames):
            parms['unique_auto_tier_policy_names'] = autotierpolicynames

        # A path is an Initiator Target combination, Is applied as a per Host
        # limit
        if(type == 'block'):
            if (maxpaths):
                parms['max_paths'] = maxpaths
            if (minpaths):
                parms['min_paths'] = minpaths
            if(pathsperinitiator is not None):
                parms['paths_per_initiator'] = pathsperinitiator

        body = json.dumps(parms)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "PUT",
                                             self.URI_VPOOL_SHOW.format(
                                                 type, vpooluri), body)
        o = common.json_decode(s)
        return o

    def vpool_delete_uri(self, type, uri):
        '''
        This function will take uri as input and deletes that particular VPOOL
        from ECS database.
        parameters:
            uri : unique resource identifier for given VPOOL name.
        return
            return with status of the delete operation.
            false incase it fails to do delete.
        '''
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             self.URI_VPOOL_DEACTIVATE.format(
                                                 type, uri),
                                             None)
        return str(s) + " ++ " + str(h)

    def vpool_delete(self, name, type):
        uri = self.vpool_query(name, type)
        res = self.vpool_delete_uri(type, uri)
        return res

    def vpool_query(self, name, type):
        '''
        This function will take the VPOOL name and type of VPOOL
        as input and get uri of the first occurance of given VPOOL.
        paramters:
             name : Name of the VPOOL.
             type : Type of the VPOOL { 'file', 'block' or 'object'}
        return
            return with uri of the given vpool.
        '''
        if (common.is_uri(name)):
            return name
        
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "GET",
            self.URI_VPOOL_SEARCH.format(type, name), None)

        o = common.json_decode(s)
        if(len(o['resource']) > 0):
            # Get the Active vpool ID.
            for vpool in o['resource']:
                if self.vpool_show_uri(type, vpool['id'], False) is not None:
                    return vpool['id']
                
        # Riase not found exception. as we did not find any active vpool.
        raise SOSError(SOSError.SOS_FAILURE_ERR, "VPOOL " + name +
                       " (" + type + ") " + ": not found")        

# VPOOL Create routines
def create_parser(subcommand_parsers, common_parser):
    # create command parser
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS VPOOL Create cli usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create a VPOOL')
    mandatory_args = create_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='Name of VPOOL',
                                metavar='<vpoolname>',
                                dest='name',
                                required=True)
    mandatory_args.add_argument('-protocol', '-pl',
                                help='Protocol used {NFS,CIFS for file; ' +
                                'FC, iSCSI for block',
                                metavar='<protocol>',
                                dest='protocol',
                                nargs='+',
                                required=True)
    mandatory_args.add_argument('-varrays', '-va',
                               help='varrays',
                               metavar='<varrays>',
                               dest='varrays',
                               nargs='+',
                               required=True)
    create_parser.add_argument('-maxsnapshots', '-msnp',
                               help='Maximum number of native snapshots',
                               metavar='<max_snapshots>',
                               dest='max_snapshots')
    create_parser.add_argument(
        '-maxcontinuouscopies', '-mcc',
        help='Maximum number of native continuous copies',
        metavar='<max_continous_copies>',
        dest='maxcontinuouscopies')
    create_parser.add_argument('-continuouscopiesvpool', '-ccv',
                               help='vpool for continous copies',
                               metavar='<continuouscopies_vpool>',
                               dest='continuouscopiesvpool')
    create_parser.add_argument('-provisiontype', '-pt',
                               help='Provision type Values can be Thin or ' +
                               'Thick(mandatory for block VPOOL)',
                               metavar='<provisiontype>',
                               dest='provisiontype')
    create_parser.add_argument('-ha',
                               help='high availability ' +
                               'eg:hatype:varray:vpool:enableRP',
                               metavar='<highavailability>',
                               dest='ha')
    create_parser.add_argument('-rp',
                               help='RP protection copies parameters, ' +
                               'eg:varray:vpool:journalsize',
                               dest='rp',
                               metavar='<rp>',
                               nargs='+')
    create_parser.add_argument('-rp_source_policy', '-rp_policy',
                               help='RP protection source policy, ' +
                               'eg:journalsize:copymode:rpovalue:rpotype',
                               dest='rp_policy',
                               metavar='<rp_source_policy>')
    create_parser.add_argument('-systemtype', '-st',
                               help='Supported System Types',
                               metavar='<systemtype>',
                               choices=StorageSystem.SYSTEM_TYPE_LIST,
                               dest='systemtype')

    create_parser.add_argument('-raidlevel', '-rl',
                               help='Posible values RAID1, RAID2, RAID3, ' +
                               'RAID4, RAID5, RAID6, RAID10',
                               metavar='<raidlevel>',
                               nargs='+',
                               dest='raidlevel')
    create_parser.add_argument('-fastpolicy', '-fp',
                               help='AutoTiering Policy Name can be ' +
                               'specified, only if SystemType is specified',
                               metavar='<fastpolicy>',
                               dest='fastpolicy')

    create_parser.add_argument('-drivetype', '-dt',
                               help='Supported Drive Types',
                               metavar='<drivetype>',
                               choices=['SSD', 'FC', 'SAS', 'NL_SAS',
                                        'SATA', 'HARD_DISK_DRIVE'],
                               dest='drivetype')

    create_parser.add_argument('-type', '-t',
                               help='Type of the VPOOL (default:file)',
                               default='file',
                               dest='type',
                               metavar='<vpooltype>',
                               choices=['file', 'block', 'object'])
    mandatory_args.add_argument('-description', '-desc',
                               help='Description of VPOOL',
                               dest='description',
                               metavar='<description>',
                               required=True)
    create_parser.add_argument('-usematchedpools', '-ump',
                               help='VPOOL uses matched pools',
                               metavar='<useMatchedPools>',
                               dest='usematchedpools',
                               choices=['true', 'false', 'True', 'False',
                                        'TRUE', 'FALSE'])
    create_parser.add_argument('-multivolconsistency', '-mvc',
                               help=' multi volume consistency',
                               action='store_true',
                               dest='multivolconsistency')

    create_parser.add_argument('-expandable', '-ex',
                               help='Indicates if non disruptive volume ' +
                               'expansion should be supported',
                               dest='expandable',
                               metavar='<expandable>',
                               choices=VirtualPool.CONDITION_TYPE)
    create_parser.add_argument('-fastexpansion', '-fe',
                               help='Indicates that vpool volumes should ' +
                               'use concatenated meta volumes not striped',
                               dest='fastexpansion',
                               metavar='<fastexpansion>',
                               choices=VirtualPool.CONDITION_TYPE)
    create_parser.add_argument(
        '-autotierpolicynames', '-apn',
        help='unique_auto_tier_policy_names for fastpolicy',
        dest='autotierpolicynames',
        metavar='<unique_auto_tier_policy_names>',
        choices=VirtualPool.CONDITION_TYPE)

    create_parser.add_argument(
        '-maxpaths', '-mxp',
        help='The maximum number of paths that can be ' +
        'used between a host and a storage volume',
        metavar='<MaxPaths>',
        dest='maxpaths',
        type=int)
    create_parser.add_argument(
        '-minpaths', '-mnp',
        help='The minimum  number of paths that can be used ' +
        'between a host and a storage volume',
        metavar='<MinPaths>',
        dest='minpaths',
        type=int)
    create_parser.add_argument(
        '-thinpreallocper', '-tpap',
        help='Thin volume preallocation percentage',
        metavar='<thinpreallocper>',
        dest='thinpreallocper',
        type=int)
    create_parser.add_argument('-pathsperinitiator', '-ppi',
                               help='The number of paths per initiator',
                               metavar='<PathsPerInitiator>',
                               dest='pathsperinitiator',
                               type=int)
    create_parser.add_argument('-srdf',
                               help='VMAX SRDF protection parameters, ' +
                               'eg:varray:vpool:policy',
                               dest='srdf',
                               metavar='<srdf>',
                               nargs='+')

    create_parser.set_defaults(func=vpool_create)


def vpool_create(args):
    try:
        if (args.rp and not args.rp_policy):
            raise SOSError(SOSError.SOS_FAILURE_ERR,
                           "Please mention -rp_policy for RP")
                
        obj = VirtualPool(args.ip, args.port)
        res = obj.vpool_create(args.name,
                               args.description,
                               args.type,
                               args.protocol,
                               args.varrays,
                               args.provisiontype,
                               args.rp,
                               args.rp_policy,
                               args.systemtype,
                               args.raidlevel,
                               args.fastpolicy,
                               args.drivetype,
                               args.expandable,
                               args.usematchedpools,
                               args.max_snapshots,
                               args.maxcontinuouscopies,
                               args.continuouscopiesvpool,
                               args.multivolconsistency,
                               args.autotierpolicynames,
                               args.ha,
                               args.minpaths,
                               args.maxpaths,
                               args.pathsperinitiator,
                               args.srdf,
                               args.fastexpansion,
                               args.thinpreallocper)
    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(SOSError.SOS_FAILURE_ERR, "VPOOL " + args.name +
                           " (" + args.type + ") " + ": Create failed\n" +
                           e.err_text)
        else:
            common.format_err_msg_and_raise("create", "vpool", e.err_text,
                                            e.err_code)

# VPOOL Update routines


def update_parser(subcommand_parsers, common_parser):
    # create command parser
    update_parser = subcommand_parsers.add_parser(
        'update',
        description='ECS VPOOL Update cli usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Update a VPOOL')
    mandatory_args = update_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='Name of VPOOL',
                                metavar='<vpoolname>',
                                dest='name',
                                required=True)

    protocol_exclgroup = update_parser.add_mutually_exclusive_group(
        required=False)
    protocol_exclgroup.add_argument('-protocol_add', '-pa',
                                    help='Protocol to be added to VPOOL',
                                    dest='protocol_add',
                                    nargs='+',
                                    metavar='<protocol_add>')
    protocol_exclgroup.add_argument('-protocol_remove', '-prm',
                                    metavar="<protocol_remove>",
                                    help='Protocol to be removed from VPOOL',
                                    nargs='+',
                                    dest='protocol_remove')

    nh_exclgroup = update_parser.add_mutually_exclusive_group(required=False)
    nh_exclgroup.add_argument('-varray_add', '-va_add',
                              help='varray to be added to VPOOL',
                              dest='varray_add',
                              nargs='+',
                              metavar='<varray_add>')
    nh_exclgroup.add_argument('-varray_remove', '-va_rm',
                              metavar="<varray_remove>",
                              help='varray to be removed from VPOOL',
                              nargs='+',
                              dest='varray_remove')

    update_parser.add_argument('-usematchedpools', '-ump',
                               help='VPOOL uses matched pools',
                               metavar='<useMatchedPools>',
                               dest='usematchedpools',
                               choices=['true', 'false', 'True', 'False',
                                        'TRUE', 'FALSE'])
    update_parser.add_argument('-label', '-l',
                               help='New name for VPOOL',
                               metavar='<label>',
                               dest='label')
    update_parser.add_argument('-ha',
                               help='high availability ' +
                               'eg:hatype:varray:vpool:enableRP',
                               metavar='<highavailability>',
                               dest='ha')
    update_parser.add_argument('-maxsnapshots', '-msnp',
                               help='Maximum number of native snapshots',
                               metavar='<max_snapshots>',
                               dest='max_snapshots')
    update_parser.add_argument('-maxcontinuouscopies', '-mcc',
                               help='Max number of native continuous copies',
                               metavar='<maxcontinuouscopies>',
                               dest='maxcontinuouscopies')
    update_parser.add_argument('-type', '-t',
                               help='Type of the VPOOL (default:file)',
                               default='file',
                               dest='type',
                               metavar='<vpooltype>',
                               choices=['file', 'block', 'object'])
    update_parser.add_argument('-description', '-desc',
                               help='Description of VPOOL',
                               dest='description',
                               metavar='<description>')
    update_parser.add_argument('-multivolconsistency', '-mvc',
                               help=' multi volume consistency',
                               metavar='<multivolconsistency>',
                               dest='multivolconsistency',
                               choices=['true', 'false'])
    update_parser.add_argument('-expandable', '-ex',
                               help='True/False Indicates if non disruptive ' +
                               'volume expansion should be supported',
                               dest='expandable',
                               metavar='<expandable>',
                               choices=VirtualPool.CONDITION_TYPE)
    update_parser.add_argument('-fastexpansion', '-fe',
                               help='Indicates that vpool volumes should ' +
                               'use concatenated meta volumes not striped',
                               dest='fastexpansion',
                               metavar='<fastexpansion>',
                               choices=VirtualPool.CONDITION_TYPE)
    update_parser.add_argument('-fastpolicy', '-fp',
                               help='Fast policy Name can be specified',
                               metavar='<fastpolicy>',
                               dest='fastpolicy')
    update_parser.add_argument('-autotierpolicynames', '-apn',
                               help='True/False to select unique auto tier ' +
                               'policy names for fastpolicy',
                               dest='autotierpolicynames',
                               metavar='<unique_auto_tier_policy_names>',
                               choices=VirtualPool.CONDITION_TYPE)

    update_parser.add_argument('-maxpaths', '-mxp',
                               help='The maximum number of paths that can ' +
                               'be used between a host and a storage volume',
                               metavar='<MaxPaths>',
                               dest='maxpaths',
                               type=int)
    update_parser.add_argument('-minpaths', '-mnp',
                               help='The minimum  number of paths that can ' +
                               'be used between a host and a storage volume',
                               metavar='<MinPaths>',
                               dest='minpaths',
                               type=int)
    update_parser.add_argument('-pathsperinitiator', '-ppi',
                               help='The number of paths per initiator',
                               metavar='<PathsPerInitiator>',
                               dest='pathsperinitiator',
                               type=int)
    update_parser.add_argument('-thinpreallocper', '-tpap',
                               help='Thin volume preallocation percentage',
                               metavar='<thinpreallocper>',
                               dest='thinpreallocper',
                               type=int)
    update_parser.add_argument('-srdf_add',
                               help='VMAX SRDF protection parameters, ' +
                               'eg:varray:vpool:policy',
                               dest='srdfadd',
                               metavar='<srdfadd>',
                               nargs='+')
    update_parser.add_argument('-srdf_remove',
                               help='VMAX SRDF protection parameters, ' +
                               'eg:varray:vpool:policy',
                               dest='srdfremove',
                               metavar='<srdfremove>',
                               nargs='+')
    update_parser.add_argument('-rp_add',
                               help='RP protection parameters, ' +
                               'eg:varray:vpool:journalsize',
                               dest='rpadd',
                               metavar='<rp_add>',
                               nargs='+')
    update_parser.add_argument('-rp_remove',
                               help='RP protection parameters, ' +
                               'eg:varray:vpool:journalsize',
                               dest='rpremove',
                               metavar='<rp_remove>',
                               nargs='+')
    update_parser.add_argument('-rp_source_policy', '-rp_policy',
                               help='RP protection source policy, ' +
                               'eg:journalsize:copymode:rpovalue:rpotype',
                               dest='rp_policy',
                               metavar='<rp_source_policy>')
    quota.add_update_parser_arguments(update_parser)
    update_parser.set_defaults(func=vpool_update)


def vpool_update(args):
    try:

        if(args.label is not None or args.description is not None or
           args.protocol_add is not None or args.protocol_remove is not None or
           args.varray_add is not None or args.varray_remove is not None or
           args.usematchedpools is not None or
           args.max_snapshots is not None or
           args.maxcontinuouscopies is not None or
           args.multivolconsistency is not None or
           args.expandable is not None or
           args.autotierpolicynames is not None or
           args.fastpolicy is not None or
           args.ha or args.minpaths is not None or
           args.maxpaths is not None or args.pathsperinitiator is not None or
           args.srdfadd is not None or args.srdfremove is not None or
           args.rp_policy is not None or
           args.fastexpansion is not None or
           args.thinpreallocper is not None or
           args.rpadd is not None or args.rpremove is not None or
           args.quota_enable is not None or args.quota_capacity is not None):
            obj = VirtualPool(args.ip, args.port)
            obj.vpool_update(args.name,
                             args.label,
                             args.description,
                             args.type,
                             args.protocol_add,
                             args.protocol_remove,
                             args.varray_add,
                             args.varray_remove,
                             args.usematchedpools,
                             args.max_snapshots,
                             args.maxcontinuouscopies,
                             args.multivolconsistency,
                             args.expandable,
                             args.autotierpolicynames,
                             args.ha,
                             args.fastpolicy,
                             args.minpaths,
                             args.maxpaths,
                             args.pathsperinitiator,
                             args.srdfadd,
                             args.srdfremove,
                             args.rp_policy,
                             args.rpadd,
                             args.rpremove,
                             args.quota_enable,
                             args.quota_capacity,
                             args.fastexpansion,
                             args.thinpreallocper)
        else:
            raise SOSError(SOSError.SOS_FAILURE_ERR,
                           "Please provide atleast one of parameters")

    except SOSError as e:
        common.format_err_msg_and_raise("update", "vpool", e.err_text,
                                        e.err_code)


# VPOOL Delete routines

def delete_parser(subcommand_parsers, common_parser):
    # delete command parser
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS VPOOL Delete CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete a VPOOL')
    mandatory_args = delete_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='name of VPOOL',
                                dest='name',
                                metavar='<vpoolname>',
                                required=True)
    delete_parser.add_argument('-type', '-t',
                               help='Type of the VPOOL (default:file)',
                               default='file',
                               dest='type',
                               metavar='<vpooltype>',
                               choices=['file', 'block', 'object'])
    delete_parser.set_defaults(func=vpool_delete)


def vpool_delete(args):
    obj = VirtualPool(args.ip, args.port)
    try:
        obj.vpool_delete(args.name, args.type)
       # return "VPOOL " + args.name + " of type " + args.type + ": Deleted"
    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(SOSError.SOS_FAILURE_ERR, "VPOOL " + args.name +
                           " (" + args.type + ") " + ": Delete failed\n" +
                           e.err_text)
        else:
            common.format_err_msg_and_raise("delete", "vpool", e.err_text,
                                            e.err_code)


# VPOOL Show routines

def show_parser(subcommand_parsers, common_parser):
    # show command parser
    show_parser = subcommand_parsers.add_parser(
        'show',
        description='ECS VPOOL Show CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show details of a VPOOL')
    mandatory_args = show_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='name of VPOOL',
                                dest='name',
                                metavar='<vpoolname>',
                                required=True)
    show_parser.add_argument('-type', '-t',
                             help='Type of VPOOL (default:file)',
                             default='file',
                             dest='type',
                             metavar='<vpooltype>',
                             choices=['file', 'block', 'object'])
    show_parser.add_argument('-xml',
                             dest='xml',
                             action='store_true',
                             help='XML response')
    show_parser.set_defaults(func=vpool_show)


def vpool_show(args):

    obj = VirtualPool(args.ip, args.port)
    try:
        res = obj.vpool_show(args.name, args.type, args.xml)
        if(args.xml):
            return common.format_xml(res)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise("show", "vpool", e.err_text,
                                        e.err_code)


# VPOOL get pools routines

def getpools_parser(subcommand_parsers, common_parser):
    # show command parser
    getpools_parser = subcommand_parsers.add_parser(
        'get_pools',
        description='ECS VPOOL Get storage pools CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get the storage pools of a VPOOL')
    mandatory_args = getpools_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='name of VPOOL',
                                dest='name',
                                metavar='<vpoolname>',
                                required=True)
    getpools_parser.add_argument('-type', '-t',
                                 help='Type of VPOOL (default:file)',
                                 default='file',
                                 dest='type',
                                 metavar='<vpooltype>',
                                 choices=['file', 'block', 'object'])
    getpools_parser.set_defaults(func=vpool_getpools)


def vpool_getpools(args):

    obj = VirtualPool(args.ip, args.port)
    try:
        pools = obj.vpool_getpools(args.name, args.type)
        if(len(pools) > 0):
            for pool in pools:
                ssobj = StorageSystem(args.ip, args.port)
                storagesys = ssobj.show_by_uri(pool['storage_system']['id'])
                pool['storagesystem_guid'] = storagesys['native_guid']
            from common import TableGenerator
            TableGenerator(pools, ['pool_name', 'supported_volume_types',
                                   'operational_status',
                                   'storagesystem_guid']).printTable()
    except SOSError as e:
        common.format_err_msg_and_raise("get_pools", "vpool", e.err_text,
                                        e.err_code)

# VPOOL refresh pools routines


def refreshpools_parser(subcommand_parsers, common_parser):
    # show command parser
    refreshpools_parser = subcommand_parsers.add_parser(
        'refresh_pools',
        description='ECS VPOOL refresh  storage pools CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Refresh assigned matched storage pools of a VPOOL')
    mandatory_args = refreshpools_parser.add_argument_group(
        'mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='name of VPOOL',
                                dest='name',
                                metavar='<vpoolname>',
                                required=True)
    refreshpools_parser.add_argument('-type', '-t',
                                     help='Type of VPOOL (default:file)',
                                     default='file',
                                     dest='type',
                                     metavar='<vpooltype>',
                                     choices=['file', 'block', 'object'])
    refreshpools_parser.set_defaults(func=vpool_refreshpools)


def vpool_refreshpools(args):

    obj = VirtualPool(args.ip, args.port)
    try:
        pools = obj.vpool_refreshpools(args.name, args.type)
        if(len(pools) > 0):
            for pool in pools:
                ssobj = StorageSystem(args.ip, args.port)
                storagesys = ssobj.show_by_uri(pool['storage_system']['id'])
                pool['storagesystem_guid'] = storagesys['native_guid']
            from common import TableGenerator
            TableGenerator(pools, ['pool_name', 'supported_volume_types',
                                   'operational_status',
                                   'storagesystem_guid']).printTable()
    except SOSError as e:
        common.format_err_msg_and_raise("refresh_pools", "vpool", e.err_text,
                                        e.err_code)

# VPOOL add pools routines


def addpools_parser(subcommand_parsers, common_parser):
    # show command parser
    addpools_parser = subcommand_parsers.add_parser(
        'add_pools',
        description='ECS VPOOL add  storage pools CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Add assigned  storage pools of a VPOOL')
    mandatory_args = addpools_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='name of VPOOL',
                                dest='name',
                                metavar='<vpoolname>',
                                required=True)
    mandatory_args.add_argument('-pools',
                                help='Pools to be added',
                                dest='pools',
                                metavar='<pools>',
                                nargs='+',
                                required=True)
    addpools_parser.add_argument('-type', '-t',
                                 help='Type of VPOOL (default:file)',
                                 default='file',
                                 dest='type',
                                 metavar='<vpooltype>',
                                 choices=['file', 'block', 'object'])
    mandatory_args.add_argument('-serialnumber', '-sn',
                                help='Native GUID of Storage System',
                                metavar='<serialnumber>',
                                dest='serialnumber',
                                required=True)
    mandatory_args.add_argument('-devicetype', '-dt',
                                help='device type',
                                dest='devicetype',
                                choices=StorageSystem.SYSTEM_TYPE_LIST,
                                required=True)
    addpools_parser.set_defaults(func=vpool_addpools)


def vpool_addpools(args):

    obj = VirtualPool(args.ip, args.port)
    try:
        res = obj.vpool_addpools(args.name, args.type,
                                 args.pools, args.serialnumber,
                                 args.devicetype)
        # return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise("add_pools", "vpool", e.err_text,
                                        e.err_code)

# VPOOL remove pools routines


def removepools_parser(subcommand_parsers, common_parser):
    # show command parser
    removepools_parser = subcommand_parsers.add_parser(
        'remove_pools',
        description='ECS VPOOL remove  storage pools CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Remove assigned  storage pools of a VPOOL')
    mandatory_args = removepools_parser.add_argument_group(
        'mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='name of VPOOL',
                                dest='name',
                                metavar='<vpoolname>',
                                required=True)
    mandatory_args.add_argument('-pools',
                                help='Pools to be removed',
                                dest='pools',
                                metavar='<pools>',
                                nargs='+',
                                required=True)
    removepools_parser.add_argument('-type', '-t',
                                    help='Type of VPOOL (default:file)',
                                    default='file',
                                    dest='type',
                                    metavar='<vpooltype>',
                                    choices=['file', 'block', 'object'])
    mandatory_args.add_argument('-serialnumber', '-sn',
                                help='Native GUID of Storage System',
                                metavar='<serialnumber>',
                                dest='serialnumber',
                                required=True)
    mandatory_args.add_argument('-devicetype', '-dt',
                                help='device type',
                                dest='devicetype',
                                choices=StorageSystem.SYSTEM_TYPE_LIST,
                                required=True)
    removepools_parser.set_defaults(func=vpool_removepools)


def vpool_removepools(args):

    obj = VirtualPool(args.ip, args.port)
    try:
        obj.vpool_removepools(args.name, args.type,
                              args.pools, args.serialnumber,
                              args.devicetype)
        # return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise("remove_pools", "vpool", e.err_text,
                                        e.err_code)


# VPOOL allow tenant  routines
def allow_parser(subcommand_parsers, common_parser):
    # allow tenant command parser
    allow_parser = subcommand_parsers.add_parser(
        'allow',
        description='ECS VPOOL Allow Tenant CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Allow Tenant to use a VPOOL')
    mandatory_args = allow_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='name of VPOOL',
                                dest='name',
                                metavar='<vpoolname>',
                                required=True)
    allow_parser.add_argument('-tenant', '-tn',
                              dest='tenant',
                              metavar='<tenant>',
                              help='Name of the Tenant')

    allow_parser.add_argument('-type', '-t',
                              help='Type of VPOOL (default:file)',
                              default='file',
                              dest='type',
                              metavar='<vpooltype>',
                              choices=['file', 'block', 'object'])
    allow_parser.set_defaults(func=vpool_allow_tenant)


def vpool_allow_tenant(args):

    obj = VirtualPool(args.ip, args.port)
    try:
        obj.vpool_allow_tenant(args.name, args.type, args.tenant)
    except SOSError as e:
        common.format_err_msg_and_raise("allow", "vpool", e.err_text,
                                        e.err_code)


# VPOOL remove tenant  routines

def disallow_parser(subcommand_parsers, common_parser):
    # allow tenant command parser
    allow_parser = subcommand_parsers.add_parser(
        'disallow',
        description='ECS VPOOL disallow  Tenant CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Remove Tenant to use a VPOOL')
    mandatory_args = allow_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='name of VPOOL',
                                dest='name',
                                metavar='<vpoolname>',
                                required=True)
    allow_parser.add_argument('-tenant', '-tn',
                              dest='tenant',
                              metavar='<tenant>',
                              help='Name of the Tenant')

    allow_parser.add_argument('-type', '-t',
                              help='Type of VPOOL (default:file)',
                              default='file',
                              dest='type',
                              metavar='<vpooltype>',
                              choices=['file', 'block', 'object'])
    allow_parser.set_defaults(func=vpool_remove_tenant)


def vpool_remove_tenant(args):

    obj = VirtualPool(args.ip, args.port)
    try:
        obj.vpool_remove_tenant(args.name, args.type, args.tenant)
    except SOSError as e:
        common.format_err_msg_and_raise("disallow", "vpool", e.err_text,
                                        e.err_code)


# VPOOL List routines

def list_parser(subcommand_parsers, common_parser):
    # list command parser
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS VPOOL List CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='List Classes of Service')
    list_parser.add_argument('-type', '-t',
                             help='Type of VPOOL',
                             dest='type',
                             metavar='<vpooltype>',
                             choices=['file', 'block', 'object'])
    list_parser.add_argument('-v', '-verbose',
                             dest='verbose',
                             help='List VPOOL with details',
                             action='store_true')
    list_parser.add_argument('-long', '-l',
                             action='store_true',
                             help='List VPOOL with details in table format',
                             dest='long')
    list_parser.set_defaults(func=vpool_list)

    list_parser.add_argument('-vdcname', '-vn',
                            help='shortID of VirtualDataCenter',
                            metavar='<vdcname>',
                            dest='vdcname')


def vpool_list(args):
    obj = VirtualPool(args.ip, args.port)

    from quota import Quota
    quota_obj = Quota(args.ip, args.port)

    try:
        if(args.type):
            types = [args.type]
        else:
            types = ['block', 'file']

        output = []
        for type in types:
            uris = obj.vpool_list(type, args.vdcname)
            if(len(uris) > 0):
                for item in obj.vpool_list_by_hrefs(uris):

                    # append quota attributes
                    quota_obj.append_quota_attributes(type + "_vpool",
                                                      item['id'], item)
                    if(args.vdcname == None):
                        tenanturis = obj.vpool_get_tenant(type, item['id'])
                        if(tenanturis):
                            tenantlist = []
                            for turi in tenanturis:
                                tenantname = obj.vpool_get_tenant_name(turi)
                                tenantlist.append(tenantname)
                            item['tenants_allowed'] = tenantlist

                    # format protection parameters
                    if(args.long is True and "high_availability" in item):
                        ha = ""
                        hatags = item['high_availability']
                        if('type' in hatags):
                            ha = ha + hatags['type']
                        if('ha_varray_vpool' in hatags):
                            hatags = hatags['ha_varray_vpool']
                            if('varray' in hatags):
                                from virtualarray import VirtualArray
                                ha = ha + ':' + VirtualArray(
                                        args.ip,
                                        args.port).varray_show(
                                        hatags['varray'])['name']
                            if('vpool' in hatags):
                                ha = ha + ':' + obj.vpool_show_uri(
                                        'block', hatags['vpool'])['name']
                            if('useAsRecoverPointSource' in hatags):
                                ha = ha + ':' + \
                                     str(hatags['useAsRecoverPointSource'])
                        item['ha'] = ha             
                    if(args.long is True and "protection" in item):
                        protection_param = item['protection']
                        if('continuous_copies' in protection_param and
                           'max_native_continuous_copies' in protection_param[
                               'continuous_copies']):
                            item['continuous_copies'] = protection_param[
                                'continuous_copies'][
                                'max_native_continuous_copies']
                        if('snapshots' in protection_param and
                           'max_native_snapshots' in
                           protection_param['snapshots']):
                            item['snapshots'] = protection_param[
                                'snapshots']['max_native_snapshots']
                        if('recoverpoint' in protection_param and
                           'copies' in protection_param['recoverpoint']):
                            rp_settings = \
                                protection_param['recoverpoint']['copies']
                            rp = ""
                            for copy in rp_settings:
                                if(len(rp) > 0):
                                    rp = rp + ','
                                if('varray' in copy):
                                    from virtualarray import VirtualArray
                                    rp = rp + VirtualArray(
                                        args.ip,
                                        args.port).varray_show(
                                        copy['varray'])['name']
                                if('vpool' in copy):
                                    rp = rp + ':' + obj.vpool_show_uri(
                                        'block', copy['vpool'])['name']
                                if('policy' in copy and
                                   'journal_size' in copy['policy']):
                                    rp = rp + ':' + \
                                        copy['policy']['journal_size']
                            item['recoverpoint'] = rp
                        if('remote_copies' in protection_param and
                           'remote_copy_settings' in
                           protection_param['remote_copies']):
                            remote_copy_settings = protection_param[
                                'remote_copies']['remote_copy_settings']
                            srdf = ""
                            for copy in remote_copy_settings:
                                if(len(srdf) > 0):
                                    srdf = srdf + ','
                                if('varray' in copy):
                                    from virtualarray import VirtualArray
                                    srdf = srdf + VirtualArray(
                                        args.ip, args.port).varray_show(
                                        copy['varray'])['name']
                                if('vpool' in copy):
                                    srdf = srdf + ':' + obj.vpool_show_uri(
                                        'block', copy['vpool'])['name']
                                if('remote_copy_mode' in copy):
                                    srdf = srdf + ':' + \
                                        copy['remote_copy_mode']
                            item['srdf'] = srdf
                    output.append(item)
        if(len(output) > 0):
            if(args.verbose is True):
                return common.format_json_object(output)
            if(args.long is True):
                from common import TableGenerator
                TableGenerator(
                    output, [
                        'name', 'module/type', 'protocols',
                        'num_paths', 'provisioning_type', 'continuous_copies',
                        'snapshots', 'recoverpoint', 'srdf', 'ha',
                        'quota_current_capacity', 'quota_gb']).printTable()

            else:
                from common import TableGenerator
                TableGenerator(output, ['name', 'module/type',
                                        'protocols']).printTable()

    except SOSError as e:
        if (e.err_code == SOSError.SOS_FAILURE_ERR):
            raise SOSError(SOSError.SOS_FAILURE_ERR, "VPOOL list failed\n" +
                           e.err_text)
        else:
            common.format_err_msg_and_raise("list", "vpool", e.err_text,
                                            e.err_code)

#
# VirtualPool Main parser routine
#


def vpool_parser(parent_subparser, common_parser):

    # main vpool parser
    parser = parent_subparser.add_parser('vpool',
                                         description='ECS VPOOL cli usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Operations on VPOOL')
    subcommand_parsers = parser.add_subparsers(help='Use one of commands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # show command parser
    show_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

    # allow tenant command parser
    allow_parser(subcommand_parsers, common_parser)

    # remove tenant command parser
    disallow_parser(subcommand_parsers, common_parser)

    # remove tenant command parser
    update_parser(subcommand_parsers, common_parser)

    # remove tenant command parser
    getpools_parser(subcommand_parsers, common_parser)

    # remove tenant command parser
    refreshpools_parser(subcommand_parsers, common_parser)

    # remove tenant command parser
    addpools_parser(subcommand_parsers, common_parser)

    # remove tenant command parser
    removepools_parser(subcommand_parsers, common_parser)

