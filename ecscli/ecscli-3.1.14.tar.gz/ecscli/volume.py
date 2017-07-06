#!/usr/bin/python

# Copyright (c) 2012-13 EMC Corporation
# All Rights Reserved

# This software contains the intellectual property of EMC Corporation
# or is licensed to EMC Corporation from third parties.  Use of this
# software and the intellectual property contained therein is expressly
# limited to the terms and conditions of the License Agreement under which
# it is provided by or on behalf of EMC.


import common
import tag
import json
from common import SOSError
from threading import Timer
from virtualarray import VirtualArray
from storagesystem import StorageSystem


class Volume(object):

    '''
    The class definition for operations on 'Volume'.
    '''
    # Commonly used URIs for the 'Volume' module
    URI_SEARCH_VOLUMES = '/block/volumes/search?project={0}'
    URI_SEARCH_VOLUMES_BY_PROJECT_AND_NAME = \
        '/block/volumes/search?project={0}&name={1}'
    URI_VOLUMES = '/block/volumes'
    URI_VOLUME = URI_VOLUMES + '/{0}'
    URI_VOLUME_CREATE = URI_VOLUMES + '?project={0}'
    URI_VOLUME_SNAPSHOTS = URI_VOLUME + '/snapshots'
    URI_VOLUME_RESTORE = URI_VOLUME + '/restore'
    URI_VOLUME_EXPORTS = URI_VOLUME + '/exports'
    URI_VOLUME_UNEXPORTS = URI_VOLUME_EXPORTS + '/{1},{2},{3}'
    URI_VOLUME_CONSISTENCYGROUP = URI_VOLUME + '/consistency-group'
    URI_PROJECT_RESOURCES = '/projects/{0}/resources'
    URI_VOLUME_TAGS = URI_VOLUME + '/tags'
    URI_BULK_DELETE = URI_VOLUMES + '/deactivate'
    URI_DEACTIVATE = URI_VOLUME + '/deactivate'
    URI_EXPAND = URI_VOLUME + '/expand'
    URI_TASK_LIST = URI_VOLUME + '/tasks'
    URI_TASK = URI_TASK_LIST + '/{1}'
    URI_TAG_VOLUME = URI_VOLUME + "/tags"
    URI_VOLUME_CHANGE_VPOOL = URI_VOLUMES + "/vpool-change"

    # Protection REST APIs
    URI_VOLUME_PROTECTION_CREATE = \
        '/block/volumes/{0}/protection/continuous'
    URI_VOLUME_PROTECTION_START = \
        '/block/volumes/{0}/protection/continuous/start'
    URI_VOLUME_PROTECTION_STOP = \
        '/block/volumes/{0}/protection/continuous/stop'
    URI_VOLUME_PROTECTION_PAUSE = \
        '/block/volumes/{0}/protection/continuous/pause'
    URI_VOLUME_PROTECTION_RESUME = \
        '/block/volumes/{0}/protection/continuous/resume'
    URI_VOLUME_PROTECTION_FAILOVER = \
        '/block/volumes/{0}/protection/continuous/failover'
    URI_VOLUME_PROTECTION_DELETE = \
        '/block/volumes/{0}/protection/continuous/deactivate'

    '''continuous copy or Mirror protection REST APIs '''
    URI_VOLUME_PROTECTION_MIRROR_LIST = \
        "/block/volumes/{0}/protection/continuous-copies"
    URI_VOLUME_PROTECTION_MIRROR_INSTANCE_START = \
        "/block/volumes/{0}/protection/continuous-copies/start"
    URI_VOLUME_PROTECTION_MIRROR_INSTANCE_STOP = \
        "/block/volumes/{0}/protection/continuous-copies/stop"
    URI_VOLUME_PROTECTION_MIRROR_INSTANCE_PAUSE = \
        "/block/volumes/{0}/protection/continuous-copies/pause"
    URI_VOLUME_PROTECTION_MIRROR_RESUME = \
        "/block/volumes/{0}/protection/continuous-copies/resume"
    URI_VOLUME_PROTECTION_MIRROR_FAILOVER = \
        "/block/volumes/{0}/protection/continuous-copies/failover"
    URI_VOLUME_PROTECTION_MIRROR_FAILOVER_TEST = \
        "/block/volumes/{0}/protection/continuous-copies/failover-test"
    URI_VOLUME_PROTECTION_MIRROR_FAILOVER_CANCEL = \
        "/block/volumes/{0}/protection/continuous-copies/failover-test-cancel"
    URI_VOLUME_PROTECTION_MIRROR_FAILOVER_SWAP = \
        "/block/volumes/{0}/protection/continuous-copies/swap"
    URI_VOLUME_PROTECTION_MIRROR_INSTANCE_DEACTIVATE = \
        "/block/volumes/{0}/protection/continuous-copies/deactivate"
    URI_VOLUME_PROTECTION_MIRROR_INSTANCE_STOP_PID = \
        "/block/volumes/{0}/protection/native/continuous-copies/{1}/stop/"

    URI_VOLUME_PROTECTION_MIRROR_MID_SHOW = \
        "/block/volumes/{0}/protection/continuous-copies/{1}"
    URI_VOLUME_PROTECTION_MIRROR_FULLCOPY = \
        "/block/volumes/{0}/protection/full-copies"

    # Protection set REST APIs
    URI_VOLUME_PROTECTIONSET_INSTANCE = \
        "/block/volumes/{0}/protection/protection-sets/{1}"
    URI_VOLUME_PROTECTIONSET_RESOURCES = '/block/protection-sets/{0}/resources'
    URI_VOLUME_PROTECTIONSET_DISCOVER = '/block/protection-sets/{0}/discover'

    URI_UNMANAGED_VOLUMES_SHOW = '/vdc/unmanaged/volumes/{0}'
    URI_UNMANAGED_VOLUMES_INGEST = '/vdc/unmanaged/volumes/ingest'

    # Protection REST APIs - clone
    URI_VOLUME_PROTECTION_FULLCOPIES = \
        '/block/volumes/{0}/protection/full-copies'
    URI_SNAPSHOT_PROTECTION_FULLCOPIES = \
        '/block/snapshots/{0}/protection/full-copies'

    VOLUME_PROTECTIONS = ['rp', 'native', 'srdf']
    VOLUME_PROTECTION_HELP = \
        'type of protection(rp or native or srdf) - default:native'

    VOLUME_PROTECTIONS_EX_SRDF = ['rp', 'native']
    VOLUME_PROTECTION_HELP_EX_SRDF = \
        'type of protection(rp or native) - default:native'

    isTimeout = False
    timeout = 300

    def __init__(self, ipAddr, port):
        '''
        Constructor: takes IP address and port of the ECS instance. These are
        needed to make http requests for REST API
        '''
        self.__ipAddr = ipAddr
        self.__port = port

    # Lists volumes in a project
    def list_volumes(self, project):
        '''
        Makes REST API call to list volumes under a project
        Parameters:
            project: name of project
        Returns:
            List of volumes uuids in JSON response payload
        '''

        from project import Project

        proj = Project(self.__ipAddr, self.__port)
        project_uri = proj.project_query(project)

        volume_uris = self.search_volumes(project_uri)
        volumes = []
        for uri in volume_uris:
            volume = self.show_by_uri(uri)
            if(volume):
                volumes.append(volume)
        return volumes

    '''
    Given the project name and volume name, the search will be performed
    to find if the volume with the given name exists or not. If found,
    the uri of the volume will be returned
    '''

    def search_by_project_and_name(self, projectName, volumeName):

        return (
            common.search_by_project_and_name(
                projectName,
                volumeName,
                Volume.URI_SEARCH_VOLUMES_BY_PROJECT_AND_NAME,
                self.__ipAddr,
                self.__port)
        )

    def search_volumes(self, project_uri):

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             Volume.URI_SEARCH_VOLUMES.format(
                                                 project_uri),
                                             None)
        o = common.json_decode(s)
        if not o:
            return []

        volume_uris = []
        resources = common.get_node_value(o, "resource")
        for resource in resources:
            volume_uris.append(resource["id"])
        return volume_uris

    # Get the list of volumes given a project uri
    def list_by_uri(self, project_uri):
        '''
        Makes REST API call and retrieves volumes based on project UUID
        Parameters:
            project_uri: UUID of project
        Returns:
            List of volumes UUIDs in JSON response payload
        '''

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            Volume.URI_PROJECT_RESOURCES.format(project_uri),
            None)
        o = common.json_decode(s)
        if not o:
            return []

        volume_uris = []
        resources = common.get_node_value(o, "project_resource")
        for resource in resources:
            if(resource["resource_type"] == "volume"):
                volume_uris.append(resource["id"])
        return volume_uris

    def protection_operations(self, volume, operation, local, remote):
        '''
        This function is to do different action on continuous protection
        for given volume
        Parameters:
            volume: Name of the volume
            operation: one of value in [ create, start, stop, pause, resume,
                                         failover or delete]
            local: true if we want local continuous protection
            remote: true, if we want rmote continuous protection
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)

        if("create" == operation):
            uri = Volume.URI_VOLUME_PROTECTION_CREATE.format(vol_uri)
        elif("start" == operation):
            uri = Volume.URI_VOLUME_PROTECTION_START.format(vol_uri)
        elif("stop" == operation):
            uri = Volume.URI_VOLUME_PROTECTION_STOP.format(vol_uri)
        elif("pause" == operation):
            uri = Volume.URI_VOLUME_PROTECTION_PAUSE.format(vol_uri)
        elif("resume" == operation):
            uri = Volume.URI_VOLUME_PROTECTION_RESUME.format(vol_uri)
        elif("failover" == operation):
            uri = Volume.URI_VOLUME_PROTECTION_FAILOVER.format(vol_uri)
        elif("delete" == operation):
            uri = Volume.URI_VOLUME_PROTECTION_DELETE.format(vol_uri)
        else:
            raise SOSError(
                SOSError.VALUE_ERR,
                "Invalid operation:" +
                operation)

        if(local):
            if ('?' in uri):
                uri += '&local=' + 'true'
            else:
                uri += '?local=' + 'true'

        if(remote):
            if ('?' in uri):
                uri += '&remote=' + 'true'
            else:
                uri += '?remote=' + 'true'

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             uri,
                                             None)

        o = common.json_decode(s)
        return o

    def mirror_protection_copyparam(
            self, volume, mirrorvol, copytype="native", sync='false'):
        copies_param = dict()
        copy = dict()
        copy_entries = []

        copy['type'] = copytype
        #true=split
        if(sync == 'true'):
            copy['sync'] = "true"
        else:
            copy['sync'] = "false"
        #for rp and srdf target volume should be provided
        if(copytype != 'native'):
            (pname, label) = common.get_parent_child_from_xpath(volume)
            copy['copyID'] = self.volume_query(pname + '/' + mirrorvol)
        else:
            copy['copyID'] = self.mirror_volume_query(volume, mirrorvol)
        copy_entries.append(copy)
        copies_param['copy'] = copy_entries
        return json.dumps(copies_param)

    def mirror_protection_create(self, volume, mirrorvolname, count, copytype,
                                                                     sync):
        '''
        Creating or attaching a name blockmirror volume to a volume name
        Parameters:
            volume: Name of the volume
            mirrorvolname: name of mirror volume or label
            count: Name of the mirror volume
            sync : synchronize the mirror true=split false=fracture
        Returns:
            result of the action.
        '''

        vol_uri = self.volume_query(volume)

        copies_param = dict()
        copy = dict()
        copy_entries = []
        #for rp and srdf target volume should be provided
        if(copytype != 'native' and mirrorvolname):
            (pname, label) = common.get_parent_child_from_xpath(volume)
            copy['copyID'] = self.volume_query(pname + '/' + mirrorvolname)
        copy['name'] = mirrorvolname
        if(count and count > 0):
            copy['count'] = count
        copy['type'] = copytype
        copy_entries.append(copy)
        copies_param['copy'] = copy_entries
        #true=split
        if(sync == 'true'):
            copy['sync'] = "true"
        else:
            copy['sync'] = "false"

        body = json.dumps(copies_param)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            Volume.URI_VOLUME_PROTECTION_MIRROR_INSTANCE_START.format(
                vol_uri),
            body)
        return common.json_decode(s)

    def mirror_protection_list(self, volume):
	'''
        block mirror list for a given volume name
        Parameters:
            volume: Name of the volume
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            Volume.URI_VOLUME_PROTECTION_MIRROR_LIST.format(vol_uri),
            None)
        o = common.json_decode(s)

        mirrorlist = []
        for uri in common.get_node_value(o, 'mirror'):
            mirrorlist.append(uri['id'])
        return mirrorlist

    def mirror_protection_show(self, volume, mirrorvol):
	'''
        show name of blockmirror details'
        Parameters:
            volume   : Name of the volume
                        mirrorvol: Name of the mirror volume

        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)
        uris = self.mirror_protection_list(volume)
        for mirror_uri in uris:
            mirvol = self.get_uri_mirror_protection_vol(vol_uri, mirror_uri)
            if(mirvol is not None and mirvol["name"] == mirrorvol):
                return mirvol

        raise SOSError(
            SOSError.NOT_FOUND_ERR,
            mirrorvol +
            " :Could not find the matching continuous_copy volume")
    '''
        get block mirror volume details by mirror volume uri
        Parameters:
            volume uri   : Name of the volume
            mirrorvol uri: Name of the mirror volume

        Returns:
            result of the action.
        '''

    def get_uri_mirror_protection_vol(self, vol_uri, mirror_uri):
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            Volume.URI_VOLUME_PROTECTION_MIRROR_MID_SHOW.format(
                vol_uri, mirror_uri),
            None)
        o = common.json_decode(s)
        if(o['inactive']):
            return None
        return o

    def mirror_protection_pause(self, volume, mirrorvol, type, sync):
	'''
        Pause continuous copies
        Parameters:
            volume    : Name of the source volume
                        mirrorvol : Name of the continous_copy or label
                        type      : type of protection
                        sync     : synchronize the mirror true=split false=fracture
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)
        body = self.mirror_protection_copyparam(volume, mirrorvol, type, sync)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            Volume.URI_VOLUME_PROTECTION_MIRROR_INSTANCE_PAUSE.format(vol_uri),
            body)
        return common.json_decode(s)

    def mirror_protection_resume(self, volume, mirrorvol, type, sync):
        '''
        Resume continuous copies
        Parameters:
            volume   : Name of the source volume
			mirrorvol: Name of the mirror volume
            type     : type of protection
            sync     : synchronize the mirror true=split false=fracture
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)
        body = self.mirror_protection_copyparam(volume, mirrorvol, type, sync)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            Volume.URI_VOLUME_PROTECTION_MIRROR_RESUME.format(vol_uri),
            body)

        return common.json_decode(s)

    def mirror_protection_failover_ops(self, volume, mirrorvol,
                                type="native", op="failover", sync='false'):
	'''
        Failover the volume protection
        Parameters:
            volume    : Source volume path
            mirrorvol : Name of the continous_copy
            type      : type of protection
            sync : synchronize the mirror true=split false=fracture
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)
        body = self.mirror_protection_copyparam(volume, mirrorvol, type, sync)

        uri = Volume.URI_VOLUME_PROTECTION_MIRROR_FAILOVER.format(vol_uri)
        if op == 'failover-test':
            uri = Volume.URI_VOLUME_PROTECTION_MIRROR_FAILOVER_TEST.format(
                  vol_uri)
        elif op == 'failover-test-cancel':
            uri = Volume.URI_VOLUME_PROTECTION_MIRROR_FAILOVER_CANCEL.format(
                  vol_uri)
        elif op == 'swap':
            uri = Volume.URI_VOLUME_PROTECTION_MIRROR_FAILOVER_SWAP.format(
                  vol_uri)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            uri,
            body)
        return common.json_decode(s)

    def mirror_protection_stop(self, volume, mirrorvol, type, sync):
        '''
        Stop continuous copies.
        Parameters:
            volume    : Name of Source volume
            mirrorvol : Name of the continous_copy
            type      : type of protection
            sync : synchronize the mirror true=split false=fracture
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)
        body = self.mirror_protection_copyparam(volume, mirrorvol, type, sync)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            Volume.URI_VOLUME_PROTECTION_MIRROR_INSTANCE_STOP.format(vol_uri),
            body)
        return common.json_decode(s)

    def mirror_protection_delete(self, volume, mirrorvol, type="native",
                                                         sync='false'):
        '''
            Delete continuous copies
        Parameters:
            volume    : source volume
                        mirrorvol : Name of the continous_copy
                        type      : type of protection
                        sync : synchronize the mirror true=split false=fracture
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)
        body = self.mirror_protection_copyparam(volume, mirrorvol, type, sync)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            Volume.URI_VOLUME_PROTECTION_MIRROR_INSTANCE_DEACTIVATE.format(
                vol_uri),
            body)
        return common.json_decode(s)

    def mirror_protection_copy(self, volume, copyname, count):
        '''
        This function is to do different action on mirror protection for
        given volume.
        Parameters:
            volume: Name of the volume
            operation: one of value in [ create, pause, list, show ,
                       delete or copy]
            mirrorvol: Name of the mirror volume
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)
        if(copyname):
            parms = {
                'name': copyname,
            }
        if(count):
            parms['count'] = count
        body = json.dumps(parms)

        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            Volume.URI_VOLUME_PROTECTION_MIRROR_FULLCOPY.format(vol_uri),
            body)
        return common.json_decode(s)

    def mirror_volume_query(self, volume, mirrorvolname):
	if (common.is_uri(mirrorvolname)):
            return mirrorvolname

        vol_uri = self.volume_query(volume)
	uris = self.mirror_protection_list(volume)
	for uri in uris:
            mirvol = self.get_uri_mirror_protection_vol(vol_uri, uri)
            if(mirvol is not None and mirvol['name'] == mirrorvolname):
                return mirvol['id']
        raise SOSError(SOSError.NOT_FOUND_ERR, "MirrorVolumeName " +
                       mirrorvolname + ": not found")

    def protectionset_show(self, volume):
	'''
        This function is to do different action on protection set for
        given volume.
        Parameters:
            volume: Name of the volume
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)
	vol = self.show_by_uri(vol_uri)
        if(vol and 'protection_set' in vol):
            (s, h) = common.service_json_request(
                self.__ipAddr, self.__port,
                "GET",
                Volume.URI_VOLUME_PROTECTIONSET_INSTANCE.format(
                    vol['protection_set']['id']),
                None)
            o = common.json_decode(s)
            if(o['inactive']):
                return None
            return o
	else:
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Volume does not have protection set Info")

    def protectionset_getresources(self, volume):
	'''
         This function is to do different action on protection set for
         given volume
        Parameters:
            volume: Name of the volume
        Returns:
            result of the action.
        '''
        vol_uri = self.volume_query(volume)
	vol = self.show_by_uri(vol_uri)
        if(vol and 'protection_set' in vol):
            (s, h) = common.service_json_request(
                self.__ipAddr, self.__port,
                "GET",
                Volume.URI_VOLUME_PROTECTIONSET_RESOURCES.format(
                    vol_uri, vol['protection_set']['id']),
                None)
            if(not common.json_decode(s)):
                return None
            return common.json_decode(s)
	else:
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Volume does not have protection set Info")

    def protectionset_discover(self, volume):
	'''
         This function is to do different action on protection set for
         given volume
        Parameters:
            volume: Name of the volume
        Returns:
            result of the action.

        '''
        vol_uri = self.volume_query(volume)
	vol = self.show_by_uri(vol_uri)
        if(vol and 'protection' in vol):
            (s, h) = common.service_json_request(
                self.__ipAddr, self.__port,
                "POST",
                Volume.URI_VOLUME_PROTECTIONSET_DISCOVER.format(
                    vol_uri, vol['protection']['id']),
                None)
	    return common.json_decode(s)
	else:
            raise SOSError(
                SOSError.SOS_FAILURE_ERR,
                "Volume does not have protection set Info")

    # Shows volume information given its name
    def show(self, name, show_inactive=False, xml=False):
        '''
        Retrieves volume details based on volume name
        Parameters:
            name: name of the volume. If the volume is under a project,
            then full XPath needs to be specified.
            Example: If VOL1 is a volume under project PROJ1, then the name
            of volume is PROJ1/VOL1
        Returns:
            Volume details in JSON response payload
        '''
        from project import Project

        if (common.is_uri(name)):
            return name
        (pname, label) = common.get_parent_child_from_xpath(name)
        if (pname is None):
            raise SOSError(SOSError.NOT_FOUND_ERR, "Volume " +
                           str(name) + ": not found")

        proj = Project(self.__ipAddr, self.__port)
        puri = proj.project_query(pname)
        puri = puri.strip()

        uris = self.search_volumes(puri)

        for uri in uris:
            volume = self.show_by_uri(uri, show_inactive)
            if (volume and 'name' in volume and volume['name'] == label):
                if(not xml):
                    return volume
                else:
                    return self.show_by_uri(volume['id'],
                                            show_inactive, xml)
        raise SOSError(SOSError.NOT_FOUND_ERR, "Volume " +
                       str(label) + ": not found")

    # Shows volume information given its uri
    def show_by_uri(self, uri, show_inactive=False, xml=False):
        '''
        Makes REST API call and retrieves volume details based on UUID
        Parameters:
            uri: UUID of volume
        Returns:
            Volume details in JSON response payload
        '''
        if(xml):
            (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                                 "GET",
                                                 Volume.URI_VOLUME.format(uri),
                                                 None, None, xml)
            return s

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             Volume.URI_VOLUME.format(uri),
                                             None)
        o = common.json_decode(s)
        if(show_inactive):
            return o
        inactive = common.get_node_value(o, 'inactive')
        if(inactive is True):
            return None
        return o

    def unmanaged_volume_ingest(self, tenant, project,
                                varray, vpool, volumes):
        '''
        This function is to ingest given unmanaged volumes
        into ECS.
        '''
        from project import Project
        proj_obj = Project(self.__ipAddr, self.__port)
        project_uri = proj_obj.project_query(tenant + "/" + project)

        from virtualpool import VirtualPool
        vpool_obj = VirtualPool(self.__ipAddr, self.__port)
        vpool_uri = vpool_obj.vpool_query(vpool, "block")

        from virtualarray import VirtualArray
        varray_obj = VirtualArray(self.__ipAddr, self.__port)
        varray_uri = varray_obj.varray_query(varray)

        request = {
            'vpool': vpool_uri,
            'varray': varray_uri,
            'project': project_uri,
            'unmanaged_volume_list': volumes
        }

        body = json.dumps(request)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "POST",
            Volume.URI_UNMANAGED_VOLUMES_INGEST,
            body)
        o = common.json_decode(s)
        return o

    def unmanaged_volume_show(self, volume):
        '''
        This function is to show the details of unmanaged volumes
        from  ECS.
        '''
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port,
            "GET",
            Volume.URI_UNMANAGED_VOLUMES_SHOW.format(volume),
            None)
        o = common.json_decode(s)
        return o

    # Creates a volume given label, project, vpool and size
    def create(self, project, label, size, varray, vpool,
               protocol, sync, number_of_volumes, thin_provisioned,
               consistencygroup):
        '''
        Makes REST API call to create volume under a project
        Parameters:
            project: name of the project under which the volume will be created
            label: name of volume
            size: size of volume
            varray: name of varray
            vpool: name of vpool
            protocol: protocol used for the volume (FC or iSCSI)
        Returns:
            Created task details in JSON response payload
        '''

        from project import Project
        proj_obj = Project(self.__ipAddr, self.__port)
        project_uri = proj_obj.project_query(project)

        from virtualpool import VirtualPool
        vpool_obj = VirtualPool(self.__ipAddr, self.__port)
        vpool_uri = vpool_obj.vpool_query(vpool, "block")

        varray_obj = VirtualArray(self.__ipAddr, self.__port)
        varray_uri = varray_obj.varray_query(varray)

        request = {
            'name': label,
            'size': size,
            'varray': varray_uri,
            'project': project_uri,
            'vpool': vpool_uri
        }
        if(protocol):
            request["protocols"] = protocol
        if(number_of_volumes and number_of_volumes > 1):
            request["count"] = number_of_volumes
        if(thin_provisioned):
            request["thinly_provisioned"] = thin_provisioned
        from consistencygroup import ConsistencyGroup
        if(consistencygroup):

            cgobj = ConsistencyGroup(self.__ipAddr, self.__port)
            (tenant, project) = common.get_parent_child_from_xpath(project)
            consuri = cgobj.consistencygroup_query(
                consistencygroup,
                project,
                tenant)
            request['consistency_group'] = consuri

        body = json.dumps(request)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             Volume.URI_VOLUMES,
                                             body)
        o = common.json_decode(s)

        if(sync):
            if(number_of_volumes < 2):
                # check task empty
                if (len(o["task"]) > 0):
                    task = o["task"][0]
                    return self.block_until_complete(task["resource"]["id"],
                                                     task["op_id"])
                else:
                    raise SOSError(
                        SOSError.SOS_FAILURE_ERR,
                        "error: task list is empty, no task response found")
        else:
            return o

    # Creates volume(s) from given source volume
    def clone(self, project, new_vol_name, number_of_volumes,
              src_vol_name, src_snap_name, sync):
        '''
        Makes REST API call to clone volume
        Parameters:
            project: name of the project under which the volume will be created
            new_vol_name: name of volume
            number_of_volumes: count of volumes
            src_vol_name: name of the source volume
            src_snap_name : name of the source snapshot
            sync: synchronous request
        Returns:
            Created task details in JSON response payload
        '''

        from snapshot import Snapshot
        snap_obj = Snapshot(self.__ipAddr, self.__port)
        is_snapshot_clone = False
        clone_uri = None
        clone_full_uri = None
        try:

            if(src_vol_name):
                clone_uri = self.volume_query(project + '/' + src_vol_name)
                clone_full_uri = \
                    Volume.URI_VOLUME_PROTECTION_FULLCOPIES.format(clone_uri)
                if(src_snap_name):
                    suri = snap_obj.snapshot_query("block", "volumes",
                                                    clone_uri, src_snap_name)
                    clone_full_uri = \
                        Volume.URI_SNAPSHOT_PROTECTION_FULLCOPIES.format(suri)
                is_snapshot_clone = True
        except SOSError as e:
            raise e

        request = {
            'name': new_vol_name,
            'type': None,
            'count': 1
        }

        if(number_of_volumes and number_of_volumes > 1):
            request["count"] = number_of_volumes

        body = json.dumps(request)
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             clone_full_uri,
                                             body)
        o = common.json_decode(s)
        if(sync):
            if(number_of_volumes < 2):
                task = o["task"][0]

                if(is_snapshot_clone):
                    return (
                        snap_obj.block_until_complete(
                            "block",
                            task["resource"]["id"],
                            task["op_id"])
                    )
                else:
                    return self.block_until_complete(task["resource"]["id"],
                                                     task["op_id"])
        else:
            return o

    # Update a volume information
    # Changed the volume vpool
    def update(self, prefix_path, name, vpool):
        '''
        Makes REST API call to update a volume information
        Parameters:
            name: name of the volume to be updated
            vpool: name of vpool
        Returns
            Created task details in JSON response payload
        '''
        namelist = []
	
	if type(name) is list:
	    namelist = name
	else:
	    namelist.append(name)

	volumeurilist = []

	for iter in namelist:
	    volume_uri = self.volume_query(prefix_path + "/" + iter)
            volumeurilist.append(volume_uri)

        from virtualpool import VirtualPool

        vpool_obj = VirtualPool(self.__ipAddr, self.__port)
        vpool_uri = vpool_obj.vpool_query(vpool, "block")

        params = {
            'vpool': vpool_uri,
            'volumes': volumeurilist
        }

        body = json.dumps(params)
	
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "POST",
            Volume.URI_VOLUME_CHANGE_VPOOL,
            body)

        o = common.json_decode(s)
        return o

    # Gets the exports info given a volume uri
    def get_exports_by_uri(self, uri):
        '''
        Makes REST API call to get exports info of a volume
        Parameters:
            uri: URI of the volume
        Returns:
            Exports details in JSON response payload
        '''
        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "GET",
                                             Volume.URI_VOLUME_EXPORTS.format(
                                                 uri),
                                             None)
        return common.json_decode(s)

    # Gets all tags of volume
    def getTags(self, name):
        '''
        Makes REST API call to update a volumes tags
        Parameters:
            name:       name of the volume
        Returns
            JSON response of current tags
        '''

        volume_uri = self.volume_query(name)
        requri = Volume.URI_VOLUME_TAGS.format(volume_uri)
        return tag.list_tags(self.__ipAddr, self.__port, requri)

    # Tag a volume information
    def tag(self, name, addtags, removetags):
        '''
        Makes REST API call to update volume tag information
        Parameters:
            name: name of the volume to be updated
            addtags : tags to be added to volume
            removetags: tags tp ne removed from volume
        '''
        volume_uri = self.volume_query(name)

        return (
            tag.tag_resource(
                self.__ipAddr,
                self.__port,
                Volume.URI_TAG_VOLUME,
                volume_uri,
                addtags,
                removetags)
        )

    # Exports a volume to a host given a volume name, initiator and hlu
    def export(self, name, protocol, initiator_port,
               initiator_node, hlu, host_id, sync):
        '''
        Makes REST API call to export volume to a host
        Parameters:
            name: Name of the volume
            protocol: Protocol used for export
            initiator_port: Port of host (WWPN for FC and IQN for ISCSI)
            initiator_node: Node of the host(WWNN for FC and IQN for ISCSI)
            hlu: host logical unit number -- should be unused on the host
            host_id: Physical address of the host
        Returns:
            Created Operation ID details in JSON response payload
        '''
        volume_uri = self.volume_query(name)
        body = json.dumps(
            {
                'protocol': protocol,
                'initiator_port': initiator_port,
                'initiator_node': initiator_node,
                'lun': hlu,
                'host_id': host_id
            }
        )

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             Volume.URI_VOLUME_EXPORTS.format(
                                                 volume_uri),
                                             body)
        o = common.json_decode(s)
        if(sync):
            return self.block_until_complete(volume_uri, o["op_id"])
        else:
            return o

    # Unexports a volume from a host given a volume name and the host name
    def unexport(self, name, initiator, protocol, hlu, sync):
        '''
        Makes REST API call to unexport volume from host
        Parameters:
            name: Name of the volume
            initiator: Port of host (combination of WWNN and WWPN for FC and
                       IQN for iSCSI)
            protocol: Protocol used for export
            hlu: host logical unit number -- should be unused on the host
        Returns:
            Created Operation ID details in JSON response payload
        '''
        volume_uri = self.volume_query(name)
        (s, h) = common.service_json_request(
            self.__ipAddr, self.__port, "DELETE",
            Volume.URI_VOLUME_UNEXPORTS.format(
                volume_uri, protocol, initiator, hlu),
            None)
        o = common.json_decode(s)

        if(sync):
            return self.block_until_complete(volume_uri, o["op_id"])
        else:
            return o

    # Deletes a volume given a volume name
    def delete(self, name, volume_name_list=None, sync=False,
               forceDelete=False, ecsonly=False):
        '''
        Deletes a volume based on volume name
        Parameters:
            name: name of volume if volume_name_list is None
                     otherwise it will be name of project
        '''
        if(volume_name_list is None):
            volume_uri = self.volume_query(name)
            return self.delete_by_uri(volume_uri, sync, forceDelete, ecsonly)
        else:
            vol_uris = []
            invalid_vol_names = ""
            for vol_name in volume_name_list:
                try:
                    volume_uri = self.volume_query(name + '/' + vol_name)
                    vol_uris.append(volume_uri)
                except SOSError as e:
                    if(e.err_code == SOSError.NOT_FOUND_ERR):
                        invalid_vol_names += vol_name + " "
                        continue
                    else:
                        raise e

            if(len(vol_uris) > 0):
                self.delete_bulk_uris(vol_uris, forceDelete, ecsonly)

            if(len(invalid_vol_names) > 0):
                raise SOSError(SOSError.NOT_FOUND_ERR, "Volumes: " +
                               str(invalid_vol_names) + " not found")

    # Deletes a volume given a volume uri
    def delete_by_uri(self, uri, sync=False,
                      forceDelete=False, ecsonly=False):
        '''
        Deletes a volume based on volume uri
        Parameters:
            uri: uri of volume
        '''
        params = ''
        if (forceDelete):
            params += '&' if ('?' in params) else '?'
            params += "force=" + "true"
        if (ecsonly == True):
            params += '&' if ('?' in params) else '?'
            params += "type=" + 'ECS_ONLY'

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                "POST",
                                Volume.URI_DEACTIVATE.format(uri) + params,
                                None)
        if(not s):
            return None
        o = common.json_decode(s)
        if(sync):
            return self.block_until_complete(o["resource"]["id"], o["op_id"])
        return o

    def delete_bulk_uris(self, uris, forceDelete, ecsonly):
        '''
        Deletes a volume based on volume uri
        Parameters:
            uri: uri of volume
        '''
        params = ''
        if (forceDelete):
            params += '&' if ('?' in params) else '?'
            params += "force=" + "true"
        if (ecsonly == True):
            params += '&' if ('?' in params) else '?'
            params += "type=" + 'ECS_ONLY'

        body = json.dumps({'id': uris})

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             Volume.URI_BULK_DELETE + params,
                                             body)
        o = common.json_decode(s)
        return o

    # Queries a volume given its name
    def volume_query(self, name):
        '''
        Makes REST API call to query the volume by name
        Parameters:
            name: name of volume
        Returns:
            Volume details in JSON response payload
        '''
        from project import Project

        if (common.is_uri(name)):
            return name

        (pname, label) = common.get_parent_child_from_xpath(name)
        if(not pname):
            raise SOSError(SOSError.NOT_FOUND_ERR,
                           "Project name  not specified")
        proj = Project(self.__ipAddr, self.__port)
        puri = proj.project_query(pname)
        puri = puri.strip()
        uris = self.search_volumes(puri)
        for uri in uris:
            volume = self.show_by_uri(uri)
            if (volume and 'name' in volume and volume['name'] == label):
                return volume['id']
        raise SOSError(SOSError.NOT_FOUND_ERR, "Volume " +
                       label + ": not found")

    # Timeout handler for synchronous operations
    def timeout_handler(self):
        self.isTimeout = True

    # Blocks the opertaion until the task is complete/error out/timeout
    def block_until_complete(self, volume_uri, task_id):
        self.isTimeout = False
        t = Timer(self.timeout, self.timeout_handler)
        t.start()
        while(True):
            out = self.show_task_by_uri(volume_uri, task_id)

            if(out):
                if(out["state"] == "ready"):
                    # cancel the timer and return
                    t.cancel()
                    break

                # if the status of the task is 'error' then cancel the timer
                # and raise exception
                if(out["state"] == "error"):
                    # cancel the timer
                    t.cancel()
                    error_message = "Please see logs for more details"
                    if("service_error" in out and
                       "details" in out["service_error"]):
                        error_message = out["service_error"]["details"]
                    raise SOSError(
                        SOSError.VALUE_ERR,
                        "Task: " +
                        task_id +
                        " is failed with error: " +
                        error_message)

            if(self.isTimeout):
                print "Operation timed out."
                self.isTimeout = False
                break
        return

    def list_tasks(self, project_name, volume_name=None, task_id=None):

        from project import Project
        proj = Project(self.__ipAddr, self.__port)
        puri = proj.project_query(project_name)
        puri = puri.strip()
        uris = self.search_volumes(puri)

        if(volume_name):
            for uri in uris:
                volume = self.show_by_uri(uri, True)
                if(volume['name'] == volume_name):
                    if(not task_id):
                        return self.show_task_by_uri(volume["id"])

                    else:
                        res = self.show_task_by_uri(volume["id"], task_id)
                        if(res):
                            return res
            raise SOSError(
                SOSError.NOT_FOUND_ERR,
                "Volume with name: " +
                volume_name +
                " not found")
        else:
            # volume_name is not given, get all tasks
            all_tasks = []
            for uri in uris:
                res = self.show_task_by_uri(uri)
                if(res and len(res) > 0):
                    all_tasks += res
            return all_tasks

    def show_task_by_uri(self, volume_uri, task_id=None):

        if(not task_id):
            (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                                 "GET",
                                                 Volume.URI_TASK_LIST.format(
                                                     volume_uri),
                                                 None)
            if (not s):
                return []
            o = common.json_decode(s)
            res = o["task"]
            return res
        else:
            (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                                 "GET",
                                                 Volume.URI_TASK.format(
                                                     volume_uri,
                                                     task_id),
                                                 None)
            if (not s):
                return None
            o = common.json_decode(s)
            return o

    def expand(self, name, new_size, sync=False):

        #volume_uri = self.volume_query(name)
        volume_detail = self.show(name)
        from decimal import Decimal
        new_size_in_gb = Decimal(Decimal(new_size) / (1024 * 1024 * 1024))
        current_size = Decimal(volume_detail["provisioned_capacity_gb"])
        if(new_size_in_gb <= current_size):
            raise SOSError(
                SOSError.VALUE_ERR,
                "error: Incorrect value of new size: " + str(new_size_in_gb) +
                " GB\nNew size must be greater than current size: " +
                str(current_size) + " GB")

        body = json.dumps({
            "new_size": new_size
        })

        (s, h) = common.service_json_request(self.__ipAddr, self.__port,
                                             "POST",
                                             Volume.URI_EXPAND.format(
                                                 volume_detail["id"]),
                                             body)
        if(not s):
            return None
        o = common.json_decode(s)

        if(sync):
            return self.block_until_complete(volume_detail["id"], o["op_id"])
        return o


# volume Create routines

def create_parser(subcommand_parsers, common_parser):
    create_parser = subcommand_parsers.add_parser(
        'create',
        description='ECS Volume Create CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Create a volume')
    mandatory_args = create_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='Name of volume',
                                metavar='<volumename>',
                                dest='name',
                                required=True)
    mandatory_args.add_argument('-size', '-s',
                                help='Size of volume: {number}[unit]. ' +
                                'A size suffix of K for kilobytes, ' +
                                ' M for megabytes, G for gigabytes, T for ' +
                                'terabytes is optional.' +
                                'Default unit is bytes.',
                                metavar='<volumesize[kKmMgGtT]>',
                                dest='size',
                                required=True)
    mandatory_args.add_argument('-project', '-pr',
                                help='Name of project',
                                metavar='<projectname>',
                                dest='project',
                                required=True)
    create_parser.add_argument('-tenant', '-tn',
                               metavar='<tenantname>',
                               dest='tenant',
                               help='Name of tenant')
    mandatory_args.add_argument('-vpool', '-vp',
                                help='Name of vpool',
                                metavar='<vpoolname>',
                                dest='vpool',
                                required=True)
    mandatory_args.add_argument('-varray', '-va',
                                help='Name of varray',
                                metavar='<varray>',
                                dest='varray',
                                required=True)
    create_parser.add_argument('-count', '-cu',
                               dest='count',
                               metavar='<count>',
                               type=int,
                               default=0,
                               help='Number of volumes to be created')
    create_parser.add_argument('-cg', '-consistencygroup',
                               help='The name of the consistency group',
                               dest='consistencygroup',
                               metavar='<consistentgroupname>')
    create_parser.add_argument('-synchronous', '-sync',
                               dest='sync',
                               help='Execute in synchronous mode',
                               action='store_true')
    create_parser.set_defaults(func=volume_create)


def volume_create(args):
    obj = Volume(args.ip, args.port)
    size = common.to_bytes(args.size)
    if(not size):
        raise SOSError(SOSError.CMD_LINE_ERR, 'error: Invalid input for -size')
    if(args.count < 0):
        raise SOSError(
            SOSError.CMD_LINE_ERR,
            'error: Invalid input for -count')
    if(args.count > 1 and args.sync):
        raise SOSError(
            SOSError.CMD_LINE_ERR,
            'error: Synchronous operation is not allowed for' +
            ' bulk creation of volumes')
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.create(
            args.tenant + "/" + args.project, args.name, size,
            args.varray, args.vpool, None, args.sync,
            args.count, None, args.consistencygroup)
#        if(args.sync == False):
#            return common.format_json_object(res)
    except SOSError as e:
        if (e.err_code in [SOSError.NOT_FOUND_ERR,
                           SOSError.ENTRY_ALREADY_EXISTS_ERR]):
            raise SOSError(e.err_code, "Create failed: " + e.err_text)
        else:
            common.format_err_msg_and_raise(
                "create",
                "volume",
                e.err_text,
                e.err_code)

# volume clone routines


def clone_parser(subcommand_parsers, common_parser):
    clone_parser = subcommand_parsers.add_parser(
        'clone',
        description='ECS Volume clone CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Clone a volume')
    mandatory_args = clone_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='Name of volume',
                                metavar='<volumename>',
                                dest='name',
                                required=True)
    mandatory_args.add_argument('-project', '-pr',
                                help='Name of project',
                                metavar='<projectname>',
                                dest='project',
                                required=True)
    clone_parser.add_argument('-tenant', '-tn',
                              metavar='<tenantname>',
                              dest='tenant',
                              help='Name of tenant')
    mandatory_args.add_argument('-source_volume', '-src_vol',
                             help='Name of source volume to be cloned',
                             metavar='<source_volume>',
                             dest='source_volume',
                             required=True)
    clone_parser.add_argument('-source_snapshot', '-src_snap',
                             help='Name of source snapshot to ' +
                             'clone volume from it',
                             metavar='<source_snapshot>',
                             dest='source_snapshot')
    clone_parser.add_argument('-count', '-cu',
                              dest='count',
                              metavar='<count>',
                              type=int,
                              default=0,
                              help='Number of volumes to be cloned')
    clone_parser.add_argument('-synchronous', '-sync',
                              dest='sync',
                              help='Execute in synchronous mode',
                              action='store_true')
    clone_parser.set_defaults(func=volume_clone)


def volume_clone(args):
    obj = Volume(args.ip, args.port)
    if(args.count > 1 and args.sync):
        raise SOSError(
            SOSError.CMD_LINE_ERR,
            'error: Synchronous operation is not allowed for ' +
            'bulk clone of volumes')
    try:
        if(not args.tenant):
            args.tenant = ""

        obj.clone(
            args.tenant +
            "/" +
            args.project,
            args.name,
            args.count,
            args.source_volume,
            args.source_snapshot,
            args.sync)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "clone",
            "volume",
            e.err_text,
            e.err_code)


# volume Update routines

def update_parser(subcommand_parsers, common_parser):
    update_parser = subcommand_parsers.add_parser(
        'update',
        description='ECS Volume Update CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Update a volume')
    mandatory_args = update_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='List of Volumes',
                                metavar='<volumename>',
				nargs='+',
                                dest='name',
                                required=True)
    update_parser.add_argument('-tenant', '-tn',
                               metavar='<tenantname>',
                               dest='tenant',
                               help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-vpool', '-vp',
                                help='Name of New vpool',
                                metavar='<vpoolname>',
                                dest='vpool',
                                required=True)

    update_parser.set_defaults(func=volume_update)


def volume_update(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.update(args.tenant + "/" + args.project , args.name,
                         args.vpool)
        # return common.format_json_object(res)
    except SOSError as e:
        if (e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(e.err_code, "Update failed: " + e.err_text)
        else:
            raise e


# Volume Delete routines

def delete_parser(subcommand_parsers, common_parser):
    delete_parser = subcommand_parsers.add_parser(
        'delete',
        description='ECS Volume Delete CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Delete a volume')
    mandatory_args = delete_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume(s)',
                                nargs='+',
                                required=True)
    delete_parser.add_argument('-tenant', '-tn',
                               metavar='<tenantname>',
                               dest='tenant',
                               help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    delete_parser.add_argument('-synchronous', '-sync',
                               dest='sync',
                               help='Execute in synchronous mode',
                               action='store_true')
    delete_parser.add_argument('-forceDelete', '-fd',
                            dest='forceDelete',
                            help='Delete volume forecibly',
                            action='store_true')
    delete_parser.add_argument('-ecsonly', '-vo',
                            dest='ecsonly',
                            help='Delete only from ECS',
                            action='store_true')

    delete_parser.set_defaults(func=volume_delete)


def volume_delete(args):
    obj = Volume(args.ip, args.port)

    if(len(args.name) > 1 and args.sync):
        raise SOSError(
            SOSError.CMD_LINE_ERR,
            "error: Synchronous operation is not allowed for bulk " +
            "deletion of volumes")
    if(not args.tenant):
        args.tenant = ""
    try:
        if(len(args.name) < 2):
            obj.delete(
                args.tenant +
                "/" +
                args.project +
                "/" +
                args.name[
                    0],
                None,
                args.sync,
                args.forceDelete, args.ecsonly)
        else:
            obj.delete(args.tenant + "/" + args.project, args.name,
                     args.forceDelete, args.ecsonly)
    except SOSError as e:
        if (e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(e.err_code, "Delete failed: " + e.err_text)
        else:
            raise common.format_err_msg_and_raise(
                "delete",
                "volume",
                e.err_text,
                e.err_code)


# Volume Export routines
def export_parser(subcommand_parsers, common_parser):
    export_parser = subcommand_parsers.add_parser(
        'export',
        description='ECS Volume Export CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Export volume to a host')
    mandatory_args = export_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    export_parser.add_argument('-tenant', '-tn',
                               metavar='<tenantname>',
                               dest='tenant',
                               help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-protocol', '-pl',
                                help='Protocol',
                                choices=["FC", "iSCSI"],
                                dest='protocol',
                                required=True)
    mandatory_args.add_argument('-initiator_port', '-inp',
                                metavar='<initiator_port>',
                                dest='initiator_port',
                                help='Port of host ' +
                                '(WWPN for FC and IQN for ISCSI)',
                                required=True)
    mandatory_args.add_argument('-initiator_node', '-inn',
                                metavar='<initiator_node>',
                                dest='initiator_node',
                                help='Initiator\'s WWNN',
                                required=True)
    mandatory_args.add_argument('-hlu', '-hlu',
                                metavar='<lun>',
                                dest='hlu',
                                help='host logical unit number - ' +
                                'should be unused on the host',
                                required=True)
    mandatory_args.add_argument('-hostid', '-ho',
                                metavar='<hostid>',
                                dest='hostid',
                                help='Physical address of the host',
                                required=True)
    export_parser.add_argument('-synchronous', '-sync',
                               dest='sync',
                               help='Execute in synchronous mode',
                               action='store_true')
    export_parser.set_defaults(func=volume_export)


def volume_export(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.export(args.tenant + "/" + args.project + "/" + args.name,
                         args.protocol, args.initiator_port,
                         args.initiator_node,
                         args.hlu, args.hostid, args.sync)
        if(args.sync is False):
            return common.format_json_object(res)

    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(
                SOSError.NOT_FOUND_ERR,
                "Export failed: " +
                e.err_text)
        else:
            raise e

# Volume UnExport routines


def unexport_parser(subcommand_parsers, common_parser):
    unexport_parser = subcommand_parsers.add_parser(
        'unexport',
        description='ECS Volume Unexport CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Unexport volume from host')
    mandatory_args = unexport_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    unexport_parser.add_argument('-tenant', '-tn',
                                 metavar='<tenantname>',
                                 dest='tenant',
                                 help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-initiator', '-in',
                                metavar='<initiator>',
                                dest='initiator',
                                help='Port of host (combination of WWNN and ' +
                                'WWPN for FC and IQN for ISCSI)',
                                required=True)
    mandatory_args.add_argument('-protocol', '-pl',
                                help='Protocol',
                                choices=["FC", "iSCSI"],
                                dest='protocol',
                                required=True)
    mandatory_args.add_argument('-hlu', '-hlu',
                                metavar='<lun>',
                                dest='hlu',
                                help='host logical unit number ' +
                                '(should be unused on the host)',
                                required=True)
    unexport_parser.add_argument('-synchronous', '-sync',
                                 dest='sync',
                                 help='Execute in synchronous mode',
                                 action='store_true')
    unexport_parser.set_defaults(func=volume_unexport)


def volume_unexport(args):
    obj = Volume(args.ip, args.port)
    if(not args.tenant):
        args.tenant = ""
    try:
        res = obj.unexport(args.tenant + "/" + args.project + "/" + args.name,
                           args.initiator, args.protocol, args.hlu, args.sync)
        if(args.sync is False):
            return common.format_json_object(res)
    except SOSError as e:
        if(e.err_code == SOSError.NOT_FOUND_ERR):
            raise SOSError(
                SOSError.NOT_FOUND_ERR,
                "Unexport failed: " +
                e.err_text)
        else:
            raise e

# Volume Show routines


def show_parser(subcommand_parsers, common_parser):
    show_parser = subcommand_parsers.add_parser('show',
                                                parents=[common_parser],
                                                conflict_handler='resolve',
                                                help='Show details of volume')
    mandatory_args = show_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    show_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    show_parser.add_argument('-xml',
                             action="store_true",
                             dest='xml',
                             help='Display in XML format')
    show_parser.set_defaults(func=volume_show)


def volume_show(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.show(args.tenant + "/" + args.project + "/" + args.name,
                       False, args.xml)
        if(args.xml):
            return common.format_xml(res)
        return common.format_json_object(res)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "show",
            "volume",
            e.err_text,
            e.err_code)


# Volume ingest routines

def unmanaged_parser(subcommand_parsers, common_parser):
    unmanaged_parser = subcommand_parsers.add_parser(
        'unmanaged',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Unmanaged volume operations')
    subcommand_parsers = unmanaged_parser.add_subparsers(
        help='Use one of the commands')

    # ingest unmanaged volume
    ingest_parser = subcommand_parsers.add_parser(
        'ingest',
        parents=[common_parser],
        conflict_handler='resolve',
        help='ingest unmanaged volumes into ECS')
    mandatory_args = ingest_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-vpool', '-vp',
                                metavar='<vpool>',
                                dest='vpool',
                                help='Name of vpool',
                                required=True)
    ingest_parser.add_argument('-tenant', '-tn',
                               metavar='<tenantname>',
                               dest='tenant',
                               help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-varray', '-va',
                                metavar='<varray>',
                                dest='varray',
                                help='Name of varray',
                                required=True)
    mandatory_args.add_argument('-volumes', '-vol',
                                metavar='<volumes>',
                                dest='volumes',
                                help='Name or id of volume',
                                nargs='+',
                                required=True)

    # show unmanaged volume
    umshow_parser = subcommand_parsers.add_parser('show',
                                                  parents=[common_parser],
                                                  conflict_handler='resolve',
                                                  help='Show unmanaged volume')
    mandatory_args = umshow_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-volume', '-vol',
                                metavar='<volume>',
                                dest='volume',
                                help='Name or id of volume',
                                required=True)

    ingest_parser.set_defaults(func=unmanaged_volume_ingest)

    umshow_parser.set_defaults(func=unmanaged_volume_show)


def unmanaged_volume_ingest(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.unmanaged_volume_ingest(args.tenant, args.project,
                                          args.varray, args.vpool,
                                          args.volumes)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "ingest",
            "unmanaged",
            e.err_text,
            e.err_code)


def unmanaged_volume_show(args):
    obj = Volume(args.ip, args.port)
    try:
        res = obj.unmanaged_volume_show(args.volume)
        return common.format_json_object(res)
    except SOSError as e:
        raise common.format_err_msg_and_raise(
            "show",
            "unmanaged",
            e.err_text,
            e.err_code)


# Volume protection routines

def protect_parser(subcommand_parsers, common_parser):
    protect_parser = subcommand_parsers.add_parser(
        'protection',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Protect operation of the volume')
    subcommand_parsers = protect_parser.add_subparsers(
        help='Use one of the commands')

    # continuous protection start
    ptstart_parser = subcommand_parsers.add_parser(
        'start',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Start continuous protection for volume')
    mandatory_args = ptstart_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    protect_parser.add_argument('-tenant', '-tn',
                                metavar='<tenantname>',
                                dest='tenant',
                                help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mutex_group2 = ptstart_parser.add_mutually_exclusive_group(required=False)
    mutex_group2.add_argument(
        '-local',
        dest='local',
        action="store_true",
        help='Local continuous protection for the volume')
    mutex_group2.add_argument('-remote',
                              dest='remote',
                              action='store_true',
                              help='Remote continuous protection for volume')

    # continuous protection stop
    ptstop_parser = subcommand_parsers.add_parser(
        'stop',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Stop continuous protection for given volume')
    mandatory_args = ptstop_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    protect_parser.add_argument('-tenant', '-tn',
                                metavar='<tenantname>',
                                dest='tenant',
                                help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mutex_group2 = ptstop_parser.add_mutually_exclusive_group(required=False)
    mutex_group2.add_argument(
        '-local',
        dest='local',
        action="store_true",
        help='Local continuous protection for the volume')
    mutex_group2.add_argument('-remote',
                              dest='remote',
                              action='store_true',
                              help='Remote continuous protection for volume')

    # pause continuous protection
    ptpause_parser = subcommand_parsers.add_parser(
        'pause',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Pause continuous protection for volume')
    mandatory_args = ptpause_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    protect_parser.add_argument('-tenant', '-tn',
                                metavar='<tenantname>',
                                dest='tenant',
                                help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mutex_group2 = ptpause_parser.add_mutually_exclusive_group(required=False)
    mutex_group2.add_argument(
        '-local',
        dest='local',
        action="store_true",
        help='Local continuous protection for the volume')
    mutex_group2.add_argument('-remote',
                              dest='remote',
                              action='store_true',
                              help='Remote continuous protection for volume')

    # resume continuous protection
    ptresume_parser = subcommand_parsers.add_parser(
        'resume',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Resume continuous protection for given volume')
    mandatory_args = ptresume_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    protect_parser.add_argument('-tenant', '-tn',
                                metavar='<tenantname>',
                                dest='tenant',
                                help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mutex_group2 = ptresume_parser.add_mutually_exclusive_group(required=False)
    mutex_group2.add_argument(
        '-local',
        dest='local',
        action="store_true",
        help='Local continuous protection for the volume')
    mutex_group2.add_argument('-remote',
                              dest='remote',
                              action='store_true',
                              help='Remote continuous protection for volume')

    # failover continuous protection
    ptfailover_parser = subcommand_parsers.add_parser(
        'failover',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Failover continuous protection for volume')
    mandatory_args = ptfailover_parser.add_argument_group(
        'mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    protect_parser.add_argument('-tenant', '-tn',
                                metavar='<tenantname>',
                                dest='tenant',
                                help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mutex_group2 = ptfailover_parser.add_mutually_exclusive_group(
        required=False)
    mutex_group2.add_argument(
        '-local',
        dest='local',
        action="store_true",
        help='Local continuous protection for the volume')
    mutex_group2.add_argument('-remote',
                              dest='remote',
                              action='store_true',
                              help='Remote continuous protection for volume')

    ptstart_parser.set_defaults(func=volume_protect_start)

    ptstop_parser.set_defaults(func=volume_protect_stop)

    ptpause_parser.set_defaults(func=volume_protect_pause)

    ptresume_parser.set_defaults(func=volume_protect_resume)

    ptfailover_parser.set_defaults(func=volume_protect_failover)


def volume_protect_create(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protection_operations(
            args.tenant + "/" + args.project + "/" + args.name,
            "create",
            args.local, args.remote)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "create",
            "protection",
            e.err_text,
            e.err_code)


def volume_protect_start(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protection_operations(
            args.tenant + "/" + args.project + "/" + args.name,
            "start",
            args.local, args.remote)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "start",
            "protection",
            e.err_text,
            e.err_code)


def volume_protect_stop(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protection_operations(
            args.tenant + "/" + args.project + "/" + args.name,
            "stop",
            args.local, args.remote)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "stop",
            "protection",
            e.err_text,
            e.err_code)


def volume_protect_pause(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protection_operations(
            args.tenant + "/" + args.project + "/" + args.name,
            "pause",
            args.local, args.remote)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "pause",
            "protection",
            e.err_text,
            e.err_code)


def volume_protect_resume(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protection_operations(
            args.tenant + "/" + args.project + "/" + args.name,
            "resume",
            args.local, args.remote)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "resume",
            "protection",
            e.err_text,
            e.err_code)


def volume_protect_failover(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protection_operations(
            args.tenant + "/" + args.project + "/" + args.name,
            "failover",
            args.local, args.remote)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "failover",
            "protection",
            e.err_text,
            e.err_code)


def volume_protect_delete(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protection_operations(
            args.tenant + "/" + args.project + "/" + args.name,
            "delete",
            args.local, args.remote)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "delete",
            "protection",
            e.err_text,
            e.err_code)

# Common parameters for contineous copies parser.
def add_protection_sub_common_parser(cc_common_parser):
    mandatory_args = cc_common_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume or Source volume name',
                                required=True)
    cc_common_parser.add_argument('-tenant', '-tn',
                                  metavar='<tenantname>',
                                  dest='tenant',
                                  help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-continuouscopyname', '-ccn',
                                metavar='<continuouscopyname>',
                                dest='continuouscopyname',
                                help='Protected volume name',
                                required=True)

# Common parameters for contineous copies parser.
def add_protection_common_parser(cc_common_parser):
    add_protection_sub_common_parser(cc_common_parser)
    cc_common_parser.add_argument('-type', '-t',
                                  help=Volume.VOLUME_PROTECTION_HELP,
                                  default='native',
                                  dest='type',
                                  metavar='<protectiontype>',
                                  choices=Volume.VOLUME_PROTECTIONS)
    cc_common_parser.add_argument('-split', '-sp',
                dest='split',
                help='synchronize the mirror',
                choices=['true', 'false'],
                required=False,
                default='false')

# Common parameters for contineous copies parser.
def add_protection_common_parser_nosrdf(cc_common_parser):
    add_protection_sub_common_parser(cc_common_parser)
    cc_common_parser.add_argument('-type', '-t',
                                  help=Volume.VOLUME_PROTECTION_HELP_EX_SRDF,
                                  default='native',
                                  dest='type',
                                  metavar='<protectiontype>',
                                  choices=Volume.VOLUME_PROTECTIONS_EX_SRDF)

    cc_common_parser.add_argument('-split', '-sp',
                dest='split',
                help='synchronize the mirror',
                choices=['true', 'false'],
                required=False,
                default='false')


# Volume protection routines
def mirror_protect_parser(subcommand_parsers, common_parser):
    mirror_protect_parser = subcommand_parsers.add_parser(
        'continuous_copies',
        description='ECS continuous_copies CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Continuous copies operations of a volume')
    subcommand_parsers = mirror_protect_parser.add_subparsers(
        help='Use one of the commands')

    # mirror protection create
    mptcreate_parser = subcommand_parsers.add_parser(
        'start',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Start Continuous copies for given volume',
        description='ECS continuous_copies create CLI usage.')
    # Add parameter from common protection parser.
    add_protection_common_parser(mptcreate_parser)
    mptcreate_parser.add_argument('-count', '-cu',
                                  metavar='<count>',
                                  dest='count',
                                  type=int,
                                  help='Maximum number of Continuous copies')

    mptcreate_parser.set_defaults(func=volume_mirror_protect_create)

    # mirror protection show
    mptshow_parser = subcommand_parsers.add_parser(
        'show',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies show CLI usage.',
        help='Show Continuous copy volume')
    # Add parameter from common protection parser.
    add_protection_sub_common_parser(mptshow_parser)
    mptshow_parser.set_defaults(func=volume_mirror_protect_show)

    # mirror protection pause
    mptpause_parser = subcommand_parsers.add_parser(
        'pause',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies pause CLI usage.',
        help='Pause Continuous copy volume')
    # Add parameter from common protection parser.
    add_protection_common_parser(mptpause_parser)
    mptpause_parser.set_defaults(func=volume_mirror_protect_pause)

    # mirror protection stop
    mptstop_parser = subcommand_parsers.add_parser(
        'stop',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies stop CLI usage.',
        help='Stop Continuous copy volume')
    # Add parameter from common protection parser.
    add_protection_common_parser_nosrdf(mptstop_parser)
    mptstop_parser.set_defaults(func=volume_mirror_protect_stop)

    # mirror protection delete
    mptdelete_parser = subcommand_parsers.add_parser(
        'delete',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies delete CLI usage.',
        help='Deactivate Continuous copy volume')
    # Add parameter from common protection parser.
    add_protection_common_parser_nosrdf(mptdelete_parser)
    mptdelete_parser.set_defaults(func=volume_mirror_protect_delete)

    # failover continuous protection
    mpfailover_parser = subcommand_parsers.add_parser(
        'failover',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies failover CLI usage.',
        help='Failover continuous protection for volume')
    # Add parameter from common protection parser.
    add_protection_common_parser(mpfailover_parser)
    mpfailover_parser.set_defaults(op='failover')
    mpfailover_parser.set_defaults(func=volume_mirror_protect_failover_ops)

    # failover-test continuous protection
    mpfailovertest_parser = subcommand_parsers.add_parser(
        'failover-test',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies failover-test CLI usage.',
        help='Failover-test continuous protection for volume')
    # Add parameter from common protection parser.
    add_protection_common_parser(mpfailovertest_parser)
    mpfailovertest_parser.set_defaults(op='failover-test')
    mpfailovertest_parser.set_defaults(func=volume_mirror_protect_failover_ops)

    # failover-test-cancel continuous protection
    mpfailovertestcancel_parser = subcommand_parsers.add_parser(
        'failover-test-cancel',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies failover-test-cancel CLI usage.',
        help='Failover-test-cancel continuous protection for volume')
    # Add parameter from common protection parser.
    add_protection_common_parser(mpfailovertestcancel_parser)
    mpfailovertestcancel_parser.set_defaults(op='failover-test-cancel')
    mpfailovertestcancel_parser.set_defaults(
        func=volume_mirror_protect_failover_ops)

    # swap continuous protection
    mpswap_parser = subcommand_parsers.add_parser(
        'swap',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies swap CLI usage.',
        help='Swap continuous protection for volume')
    # Add parameter from common protection parser.
    add_protection_common_parser(mpswap_parser)
    mpswap_parser.set_defaults(op='swap')
    mpswap_parser.set_defaults(func=volume_mirror_protect_failover_ops)

    # mirror protection list
    mptlist_parser = subcommand_parsers.add_parser(
        'list',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies list CLI usage.',
        help='List continous copies for given volume')
    mandatory_args = mptlist_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    mptlist_parser.add_argument('-tenant', '-tn',
                                metavar='<tenantname>',
                                dest='tenant',
                                help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)

    mptlist_parser.set_defaults(func=volume_mirror_protect_list)

        # copy continuous protection
    mptcopy_parser = subcommand_parsers.add_parser(
        'copy',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies copy CLI usage.',
        help='Copy full copy of volume or local copy of a volume')
    mandatory_args = mptcopy_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume or Source volume name',
                                required=True)
    mptcopy_parser.add_argument('-tenant', '-tn',
                                metavar='<tenantname>',
                                dest='tenant',
                                help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)

    mandatory_args.add_argument('-copyname', '-cp',
                                metavar='<volumecopyname>',
                                dest='copyname',
                                help='Name of copy volume',
                                required=True)
    mptcopy_parser.add_argument('-count', '-cu',
                                metavar='<count>',
                                dest='count',
                                type=int,
                                help='Number of copies')

    mptcopy_parser.set_defaults(func=volume_mirror_protect_copy)

    # mirror protection resume
    mptresume_parser = subcommand_parsers.add_parser(
        'resume',
        parents=[common_parser],
        conflict_handler='resolve',
        description='ECS continuous_copies resume CLI usage.',
        help='Resume Continuous copy volume')
    # Add parameter from common protection parser.
    add_protection_common_parser(mptresume_parser)
    mptresume_parser.set_defaults(func=volume_mirror_protect_resume)


def volume_mirror_protect_create(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        fullpathvol = args.tenant + "/" + args.project + "/" + args.name

        obj.mirror_protection_create(
            fullpathvol,
            args.continuouscopyname,
            args.count,
            args.type,
            args.split)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "start",
            "continuous_copies",
            e.err_text,
            e.err_code)


def volume_mirror_protect_delete(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""

        fullpathvol = args.tenant + "/" + args.project + "/" + args.name
        obj.mirror_protection_delete(
            fullpathvol,
            args.continuouscopyname,
            args.type,
            args.split)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "delete",
            "continuous_copies",
            e.err_text,
            e.err_code)


def volume_mirror_protect_failover_ops(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        fullpathvol = args.tenant + "/" + args.project + "/" + args.name

        obj.mirror_protection_failover_ops(
            fullpathvol,
            args.continuouscopyname,
            args.type,
            args.op,
            args.split)

    except SOSError as e:
        common.format_err_msg_and_raise(
            args.op,
            "continuous_copies",
            e.err_text,
            e.err_code)


def volume_mirror_protect_stop(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        fullpathvol = args.tenant + "/" + args.project + "/" + args.name

        obj.mirror_protection_stop(
            fullpathvol,
            args.continuouscopyname,
            args.type,
            args.split)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "stop",
            "continuous_copies",
            e.err_text,
            e.err_code)


def volume_mirror_protect_list(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.mirror_protection_list(
            args.tenant +
            "/" +
            args.project +
            "/" +
            args.name)

        mirrorlist = []
        vol_uri = obj.volume_query(
            args.tenant +
            "/" +
            args.project +
            "/" +
            args.name)
        for mirr_uri in res:
            protectobj = obj.get_uri_mirror_protection_vol(vol_uri, mirr_uri)
            nhid = None
            if(protectobj is not None):
                if("source" in protectobj and "name" in protectobj["source"]):
                    del protectobj["source"]["name"]
                if(protectobj['varray']):
                    nh = VirtualArray(
                        args.ip,
                        args.port).varray_show(protectobj['varray']['id'])
                    if(nh is not None):
                        protectobj['varray_name'] = nh['name']
                if(protectobj['source']):
                    vol = obj.show_by_uri(protectobj['source']['id'])
                    if(vol is not None):
                        protectobj['source_volume'] = vol['name']
                if(protectobj['storage_controller']):
                    storagesys = StorageSystem(
                        args.ip,
                        args.port).show_by_uri(
                        protectobj['storage_controller'])
                    if(storagesys):
                        protectobj['storagesystem_name'] = storagesys['name']
                mirrorlist.append(protectobj)
        if(len(mirrorlist) > 0):
            from common import TableGenerator
            TableGenerator(
                mirrorlist,
                ['name',
                 'source_volume',
                 'varray_name',
                 'protocols',
                 'storagesystem_name']).printTable()

    except SOSError as e:
        raise common.format_err_msg_and_raise(
            "list",
            "continuous_copies",
            e.err_text,
            e.err_code)


def volume_mirror_protect_show(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        fullpathvol = args.tenant + "/" + args.project + "/" + args.name
        res = obj.mirror_protection_show(fullpathvol, args.continuouscopyname)
        return common.format_json_object(res)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "show",
            "continuous_copies",
            e.err_text,
            e.err_code)


def volume_mirror_protect_pause(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""

        fullpathvol = args.tenant + "/" + args.project + "/" + args.name
        obj.mirror_protection_pause(
            fullpathvol,
            args.continuouscopyname,
            args.type,
            args.split)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "pause",
            "continuous_copies",
            e.err_text,
            e.err_code)


def volume_mirror_protect_resume(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        #mirror sync

        fullpathvol = args.tenant + "/" + args.project + "/" + args.name
        obj.mirror_protection_resume(
            fullpathvol,
            args.continuouscopyname,
            args.type,
            args.split)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "resume",
            "continuous_copies",
            e.err_text,
            e.err_code)


def volume_mirror_protect_copy(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        fullpathvol = args.tenant + "/" + args.project + "/" + args.name
        obj.mirror_protection_copy(fullpathvol, args.copyname, args.count)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "copy",
            "continuous_copies",
            e.err_text,
            e.err_code)


# Volume protection set routines

def protectionset_parser(subcommand_parsers, common_parser):
    protectionset_parser = subcommand_parsers.add_parser(
        'protectionset',
        description='ECS protectionset CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Protectionset operations of the volume')
    subcommand_parsers = protectionset_parser.add_subparsers(
        help='Use one of the commands')

    '''# protection set get resources
    psresources_parser = subcommand_parsers.add_parser(
        'get_resources',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Get the resources for volume protection set')

    mandatory_args = psresources_parser.add_argument_group(
        'mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    psresources_parser.add_argument('-tenant', '-tn',
                                    metavar='<tenantname>',
                                    dest='tenant',
                                    help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)

    psresources_parser.set_defaults(func=volume_protectionset_getresources)'''

    # protection set show
    psshow_parser = subcommand_parsers.add_parser(
        'show',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show volume protection set')

    mandatory_args = psshow_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    psshow_parser.add_argument('-tenant', '-tn',
                               metavar='<tenantname>',
                               dest='tenant',
                               help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)

    psshow_parser.set_defaults(func=volume_protectionset_show)

    '''# protection set discover
    psdiscover_parser = subcommand_parsers.add_parser(
        'discover',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Discover volume protection set')

    mandatory_args = psdiscover_parser.add_argument_group(
        'mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    psdiscover_parser.add_argument('-tenant', '-tn',
                                   metavar='<tenantname>',
                                   dest='tenant',
                                   help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)

    psdiscover_parser.set_defaults(func=volume_protectionset_discover)


def volume_protectionset_getresources(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protectionset_getresources(
            args.tenant +
            "/" +
            args.project +
            "/" +
            args.name)

        if(res is not None):
            return common.format_json_object(res)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "get_resources",
            "protectionset",
            e.err_text,
            e.err_code)


def volume_protectionset_discover(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protectionset_discover(
            args.tenant +
            "/" +
            args.project +
            "/" +
            args.name)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "discover",
            "protectionset",
            e.err_text,
            e.err_code)'''


def volume_protectionset_show(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.protectionset_show(
            args.tenant +
            "/" +
            args.project +
            "/" +
            args.name)
        return common.format_json_object(res)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "show",
            "protectionset",
            e.err_text,
            e.err_code)


# Volume List routines

def list_parser(subcommand_parsers, common_parser):
    list_parser = subcommand_parsers.add_parser(
        'list',
        description='ECS Volume List CLI usage',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Lists volumes under a project')
    mandatory_args = list_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    list_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    list_parser.add_argument('-verbose', '-v',
                             dest='verbose',
                             help='List volumes with details',
                             action='store_true')
    list_parser.add_argument('-long', '-l',
                             dest='long',
                             help='List volumes having more headers',
                             action='store_true')
    list_parser.set_defaults(func=volume_list)


def volume_list(args):
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        output = obj.list_volumes(args.tenant + "/" + args.project)
        if(len(output) > 0):
            if(args.verbose is False):
                for record in output:
                    if("project" in record and "name" in record["project"]):
                        del record["project"]["name"]
                    if("vpool" in record and "vpool_params" in record["vpool"]
                       and record["vpool"]["vpool_params"]):
                        for vpool_param in record["vpool"]["vpool_params"]:
                            record[vpool_param["name"]] = vpool_param["value"]
                        record["vpool"] = None
                # show a short table
                from common import TableGenerator
                if(not args.long):
                    TableGenerator(output, ['name', 'provisioned_capacity_gb',
                                            'protocols']).printTable()
                else:
                    TableGenerator(output, ['name', 'provisioned_capacity_gb',
                                            'protocols', 'thinly_provisioned',
                                            'tags']).printTable()
            else:
                return common.format_json_object(output)
        else:
            return
    except SOSError as e:
        common.format_err_msg_and_raise(
            "list",
            "volume",
            e.err_text,
            e.err_code)


def task_parser(subcommand_parsers, common_parser):
    task_parser = subcommand_parsers.add_parser(
        'tasks',
        description='ECS Volume List tasks CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Show details of volume tasks')
    mandatory_args = task_parser.add_argument_group('mandatory arguments')

    task_parser.add_argument('-tenant', '-tn',
                             metavar='<tenantname>',
                             dest='tenant',
                             help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    task_parser.add_argument('-name', '-n',
                             dest='name',
                             metavar='<volumename>',
                             help='Name of volume')
    task_parser.add_argument('-id',
                             dest='id',
                             metavar='<opid>',
                             help='Operation ID')
    task_parser.add_argument('-v', '-verbose',
                             dest='verbose',
                             action="store_true",
                             help='List all tasks')

    task_parser.set_defaults(func=volume_list_tasks)


def volume_list_tasks(args):
    if(args.id and not args.name):
        raise SOSError(SOSError.CMD_LINE_ERR,
                       "error: value for -n/-name must be provided " +
                       "when -id is used")
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        if(args.id):
            res = obj.list_tasks(
                args.tenant +
                "/" +
                args.project,
                args.name,
                args.id)
            if(res):
                return common.format_json_object(res)
        elif(args.name):
            res = obj.list_tasks(args.tenant + "/" + args.project, args.name)
            if(res and len(res) > 0):
                if(args.verbose):
                    return common.format_json_object(res)
                else:
                    from common import TableGenerator
                    TableGenerator(
                        res, ["op_id", "name", "state"]).printTable()
        else:
            res = obj.list_tasks(args.tenant + "/" + args.project)
            if(res and len(res) > 0):
                if(not args.verbose):
                    from common import TableGenerator
                    TableGenerator(
                        res, ["op_id", "name", "state"]).printTable()
                else:
                    return common.format_json_object(res)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "tasks",
            "volume",
            e.err_text,
            e.err_code)


def expand_parser(subcommand_parsers, common_parser):
    expand_parser = subcommand_parsers.add_parser('expand',
                                                  parents=[common_parser],
                                                  conflict_handler='resolve',
                                                  help='Expand volume')
    mandatory_args = expand_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                metavar='<volumename>',
                                dest='name',
                                help='Name of Volume',
                                required=True)
    expand_parser.add_argument('-tenant', '-tn',
                               metavar='<tenantname>',
                               dest='tenant',
                               help='Name of tenant')
    mandatory_args.add_argument('-project', '-pr',
                                metavar='<projectname>',
                                dest='project',
                                help='Name of project',
                                required=True)
    mandatory_args.add_argument('-size', '-s',
                                help='New size of volume: {number}[unit]. ' +
                                'A size suffix of K for kilobytes, ' +
                                'M for megabytes, G for gigabytes, ' +
                                'T for terabytes is optional.' +
                                'Default unit is bytes.',
                                metavar='<volumesize[kKmMgGtT]>',
                                dest='size',
                                required=True)
    expand_parser.add_argument('-synchronous', '-sync',
                               dest='sync',
                               help='Execute in synchronous mode',
                               action='store_true')
    expand_parser.set_defaults(func=volume_expand)


def volume_expand(args):
    size = common.to_bytes(args.size)
    if(not size):
        raise SOSError(SOSError.CMD_LINE_ERR,
                       'error: Invalid input for -size')
    obj = Volume(args.ip, args.port)
    try:
        if(not args.tenant):
            args.tenant = ""
        res = obj.expand(args.tenant + "/" + args.project +
                         "/" + args.name, size, args.sync)
    except SOSError as e:
        common.format_err_msg_and_raise(
            "expand",
            "volume",
            e.err_text,
            e.err_code)


def tag_parser(subcommand_parsers, common_parser):
    tag_parser = subcommand_parsers.add_parser(
        'tag',
        description='ECS Volume Tag CLI usage.',
        parents=[common_parser],
        conflict_handler='resolve',
        help='Tag a volume')
    mandatory_args = tag_parser.add_argument_group('mandatory arguments')
    mandatory_args.add_argument('-name', '-n',
                                help='Name of volume',
                                metavar='<volumename>',
                                dest='name',
                                required=True)
    tag_parser.add_argument('-tenant', '-tn',
                            metavar='<tenantname>',
                            dest='tenant',
                            help='Name of tenant')

    tag.add_mandatory_project_parameter(mandatory_args)

    tag.add_tag_parameters(tag_parser)

    tag_parser.set_defaults(func=volume_tag)


def volume_tag(args):
    obj = Volume(args.ip, args.port)
    try:
        if(args.add is None and args.remove is None):
            raise SOSError(SOSError.CMD_LINE_ERR,
                           "ecscli volume tag: error: at least one of " +
                           "the arguments -add -remove is required")

        if(not args.tenant):
            args.tenant = ""

        res = obj.tag(args.tenant + "/" + args.project +
                      "/" + args.name, args.add, args.remove)

    except SOSError as e:
        common.format_err_msg_and_raise(
            "volume",
            "tag",
            e.err_text,
            e.err_code)


#
# Volume Main parser routine
#
def volume_parser(parent_subparser, common_parser):
    # main project parser

    parser = parent_subparser.add_parser('volume',
                                         description='ECS Volume CLI usage',
                                         parents=[common_parser],
                                         conflict_handler='resolve',
                                         help='Operations on Volume')
    subcommand_parsers = parser.add_subparsers(help='Use one of subcommands')

    # create command parser
    create_parser(subcommand_parsers, common_parser)

    # Clone command parser
    clone_parser(subcommand_parsers, common_parser)

    # update command parser
    update_parser(subcommand_parsers, common_parser)

    # delete command parser
    delete_parser(subcommand_parsers, common_parser)

    # show command parser
    show_parser(subcommand_parsers, common_parser)

    # export command parser
    # export_parser(subcommand_parsers, common_parser)

    # unexport command parser
    # unexport_parser(subcommand_parsers, common_parser)

    # list command parser
    list_parser(subcommand_parsers, common_parser)

    # expand volume parser
    expand_parser(subcommand_parsers, common_parser)

    # task list command parser
    task_parser(subcommand_parsers, common_parser)

    # protection  command parser
    #protect_parser(subcommand_parsers, common_parser)

    # mirror protection  command parser
    mirror_protect_parser(subcommand_parsers, common_parser)

    # protection set  command parser
    protectionset_parser(subcommand_parsers, common_parser)

    # unmanaged volume  command parser
    unmanaged_parser(subcommand_parsers, common_parser)

    tag_parser(subcommand_parsers, common_parser)
