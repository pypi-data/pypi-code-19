#!/bin/env python
__author__ = "John Hover"
__copyright__ = "2017 John Hover"
__credits__ = []
__license__ = "GPL"
__version__ = "0.9.1"
__maintainer__ = "John Hover"
__email__ = "jhover@bnl.gov"
__status__ = "Production"

import ast
import base64
import json
import logging
import os
import sys
import yaml
import StringIO
import ConfigParser

from entities import User, Project, Resource, Allocation, Nodeset, Request, Cluster, Environment
from vc3infoservice import infoclient
from vc3infoservice.infoclient import  InfoMissingPairingException, InfoConnectionFailure

class VC3ClientAPI(object):
    '''
    Client application programming interface. 
    
    -- DefineX() methods return object. CreateX() stores it to infoservice. The two steps will allow 
    some manipulation of the object by the client, or calling user. 
    
    -- Oriented toward exposing only valid operations to external
    user (portal, resource tool, or admin CLI client). 
    
    -- Direct manipulations of stored information in the infoservice is only done by Entity objects, not
    client user.
        
    -- Store method (inside of storeX methods) takes infoclient arg in order to allow multiple infoservice instances in the future. 
        
    '''
    
    def __init__(self, config):
        self.config = config
        self.ic = infoclient.InfoClient(self.config)
        self.log = logging.getLogger() 


    ################################################################################
    #                           User-related calls
    ################################################################################
    def defineUser(self,   
                   name,
                   first,
                   last,
                   email,
                   institution,
                   identity_id = None):           
        '''
       Defines a new User object for usage elsewhere in the API. 
              
       :param str name: The unique VC3 username of this user
       :param str first: User's first name
       :param str last: User's last name
       :param str email: User's email address
       :param str institution: User's intitutional affiliation or employer
       :return: User  A valid User object
       
       :rtype: User        
        '''
        u = User( name=name, 
                  state='new', 
                  acl=None, 
                  first=first, 
                  last=last, 
                  email=email, 
                  institution=institution,
                  identity_id=identity_id)
        self.log.debug("Creating user object: %s " % u)
        return u
    
        
    def storeUser(self, user):
        '''
        Stores the provided user in the infoservice. 
        :param User u:  User to add. 
        :return: None
        '''
        user.store(self.ic)
          

    def listUsers(self):
        '''
        Returns list of all valid users as a list of User objects. 

        :return: return description
        :rtype: List of User objects. 
        
        '''
        return self._listEntities('User')
       
    def getUser(self, username):
        return self._getEntity('User', username)
    
    ################################################################################
    #                           Project-related calls
    ################################################################################  
    def defineProject(self, name, owner, members):
        '''
        Defines a new Project object for usage elsewhere in the API. 
              
        :param str name: The unique VC3 name of this project
        :param str owner:  The VC3 user name of the owner of this project
        :param List str:  List of VC3 user names of members of this project.  
        :return: Project  A valid Project object
        :rtype: Project        
        '''
        p = Project( name=name, 
                     state='new', 
                     acl=None, 
                     owner=owner, 
                     members=members)
        self.log.debug("Creating project object: %s " % p)
        return p
    
    
    def storeProject(self, project):
        '''
        Stores the provided project in the infoservice. 
        
        :param Project project:  Project to add. 
        :return: None
        '''
        self.log.debug("Storing project %s" % project)
        project.store(self.ic)
        self.log.debug("Done.")
    
    
    def addUserToProject(self, project, user):
        '''
        :param str project
        :param str user
        
        
        '''
        self.log.debug("Looking up user %s project %s " % (user, project))
        po = self.getProject(project)
        self.log.debug("Adding user %s to project object %s " % (user, po))
        po.addUser(user)
        self.storeProject(po)        

    def addAllocationToProject(self, allocation, projectname ):
        po = self.getProject(projectname)
        if allocation not in po.allocations:
            po.allocations.append(allocation)
        self.storeProject(po)
        
    
    def removeAllocationFromProject(self, allocation, projectname):
        po = self.getProject(projectname)
        if allocation in po.allocations:
            po.allocations.remove(allocation)
        self.storeProject(po)

    def listProjects(self):
        return self._listEntities('Project')
       
    def getProject(self, projectname):
        return self._getEntity('Project', projectname)

    def getProjectsOfOwner(self, ownername):
        projects = self.listProjects()
        filtered = [ p for p in projects if ownername == p.owner ]
        return filtered

    def getProjectsOfUser(self, username):
        projects = self.listProjects()
        filtered = [ p for p in projects if username in p.members ]
        return filtered
    

        
    ################################################################################
    #                           Resource-related calls
    ################################################################################    
    def defineResource(self, 
                       name,
                       owner, 
                       accesstype, 
                       accessmethod, 
                       accessflavor,
                       accesshost, 
                       accessport,  
                       gridresource, 
                       mfa):
        '''
        Defines a new Resource object for usage elsewhere in the API. 
              
        :param str name: The unique VC3 name of this resource
        :param str owner:  The VC3 user name of the owner of this project
        :param str resourcetype,  # grid remote-batch local-batch cloud
        :param str accessmethod,  # ssh, gsissh,  
        :param str accessflavor,  # htcondor-ce, slurm, sge, ec2, nova, gce
        :param str accesshost,    # DNS hostname
        :param str accessport,    # 22 , 6918, 8773
        :param gridresource,      # http://cldext02.usatlas.bnl.gov:8773/services/Cloud  | HTCondorCE hostname             
        :param Boolean mfa        # Does site need head-node factory?     
        :return: Resource          A valid Project object
        :rtype: Resource        
        
        '''
        r = Resource( name, 
                      state='new', 
                      acl=None, 
                      owner=owner, 
                      accesstype=accesstype, 
                      accessmethod=accessmethod, 
                      accessflavor=accessflavor, 
                      accesshost = accesshost,
                      accessport = accessport,
                      gridresource=gridresource, 
                      mfa=mfa )
        self.log.debug("Creating Resource object: %s " % r)
        return r
    
    
    def storeResource(self, resource):
        resource.store(self.ic)
    
    def listResources(self):
        return self._listEntities('Resource')
       
    def getResource(self, resourcename):
        return self._getEntity('Resource', resourcename)

    ################################################################################
    #                           Allocation-related calls
    ################################################################################ 
    def defineAllocation(self, name,
                               owner, 
                               resource, 
                               accountname,

                               ):
        '''
          
        '''
        ao = Allocation(name, 
                        state='new', 
                        acl=None, 
                        owner=owner, 
                        resource=resource, 
                        accountname=accountname)
        self.log.debug("Creating Allocation object: %s " % ao)
        return ao
    
    def storeAllocation(self, allocation):
        allocation.store(self.ic)
        
    def listAllocations(self):
        return self._listEntities('Allocation')
       
    def getAllocation(self, allocationname):
        return self._getEntity('Allocation', allocationname)

            
    ################################################################################
    #                        Cluster-related calls
    ################################################################################ 
        '''
        Defines a new Cluster (description) object for usage elsewhere in the API. 
              
        :param str name: The unique name of this cluster description.
        :param str owner:  The user name of the owner of this project
        :param [str]:   List of strings, names of nodesets in this cluster    
        :return: Cluster          A valid Cluster object
        :rtype: Cluster        
        
        '''
    def defineCluster(self, 
                      name, 
                      owner, 
                      nodesets=[] ): 
        
        c = Cluster(name=name, 
                    state='new',
                    owner=owner,
                    acl=None,
                    nodesets=nodesets, # list of names of nodesets in this cluster definition. 
                     )
        return c
                    
    def storeCluster(self, cluster):
        cluster.store(self.ic)
    
    def listClusters(self):
        return self._listEntities('Cluster')
       
    def getCluster(self, clustername):
        return self._getEntity('Cluster', clustername)
    

    ################################################################################
    #                        Nodeset-related calls
    ################################################################################ 
    def defineNodeset(self, name, owner, node_number, app_type, app_role):
        ns = Nodeset( name=name, 
                      state='new',
                      owner=owner, 
                      acl=None, 
                       
                      node_number=node_number, 
                      app_type=app_type, 
                      app_role=app_role,

                      cores=1, 
                      memory_mb=None, 
                      storage_mb=None, 
                      app_host = None, 
                      app_port = None,
                      app_sectoken = None
                       )
        self.log.debug("Created Nodeset object: %s" % ns)
        return ns 
    
    def addNodesetToCluster(self, nodesetname, clustername):
        co = self.getCluster(clustername)
        if nodesetname not in co.nodesets:
            co.nodesets.append(nodesetname)
        self.storeCluster(co)
       
    def removeNodesetFromCluster(self, nodesetname, clustername):
        co = self.getCluster(clustername)
        if nodesetname in co.nodesets:
             co.nodesets.remove(nodesetname)
        self.storeCluster(co)
        
    def listNodesets(self):
        return self._listEntities('Nodeset')
       
    def getNodeset(self, clustername):
        return self._getEntity('Nodeset', nodesetname)
    
    def storeNodeset(self, nodeset):
        nodeset.store(self.ic)

    ################################################################################
    #                        Environment-related calls
    ################################################################################ 
    def defineEnvironment(self, name, owner, packagelist = [], files={}, envmap = []):
        e = Environment(name, 
                        state='new', 
                        acl=None, 
                        owner = owner, 
                        packagelist = packagelist, 
                        files = files, 
                        envmap = envmap)
        self.log.debug("Creating Environment object: %s " % e)
        return e
    
    def storeEnvironment(self, environment):
        environment.store(self.ic)
    
    def listEnvironments(self):
        return self._listEntities('Environment')
       
    def getEnvironment(self, environmentname):
        return self._getEntity('Environment', environmentname)

    ################################################################################
    #                        Request-related calls
    ################################################################################ 
    def defineRequest(self, 
                      name, 
                      owner,
                      cluster,
                      allocations,  
                      environments, 
                      policy, 
                      expiration ):
        '''
        
        :return Request
        
        '''
        r = Request(name, 
                    state='new', 
                    acl=None,
                    owner=owner,
                    action='new',
                    state_reason='new',
                    cluster_state='new',          # state of virtual cluster this Request represents 
                    cluster_state_reason='new',
                    cluster = cluster,           # name of abstract cluster specification
                    allocations = allocations,   # list of allocation names
                    environments = environments, # list of environment names
                    policy = policy, 
                    expiration = expiration
                    )
        self.log.debug("Creating Request object: %s " % r)
        return r
    
    def storeRequest(self, request):
        request.store(self.ic)


    def listRequests(self):
        return self._listEntities('Request')
       
    def getRequest(self, requestname):
        return self._getEntity('Request', requestname)

    def saveRequestAsBlueprint(self, requestid, newlabel):
        '''
        Take the specified request and store it as a re-usable blueprint with new label
        '''
        pass
    
    
    ################################################################################
    #                        Infrastructural calls
    ################################################################################ 
    def getQueuesConf(self, requestname, queuename):
        '''
        Get the queues.conf sections for the specified request and queuename
        '''
        r = self.getRequest(requestname)

        if not r:
            raise MissingDependencyException(name = requestname, entityclass = 'Request')

        if not r.queuesconf:
            raise Exception('Request %s does not have a queues.conf defined' % requestname)

        try:
            buf   = StringIO.StringIO(self.decode(r.queuesconf))
            qconf = ConfigParser.ConfigParser()
            qconf.readfp(buf)

            return qconf.items(queuename)

        except Exception, e:
            self.log.error('Error decoding queues.conf of request %s' % requestname)
            raise e

    def getAuthConf(self, requestname, queuename):
        '''
        Get the auth.conf sections for the specified request and queuename
        '''
        r = self.getRequest(requestname)

        if not r:
            raise MissingDependencyException(name = requestname, entityclass = 'Request')

        if not r.authconf:
            raise Exception('Request %s does not have a auth.conf defined' % requestname)

        try:
            buf   = StringIO.StringIO(self.decode(r.authconf))
            aconf = ConfigParser.ConfigParser()
            aconf.readfp(buf)

            return aconf.items(queuename)

        except Exception, e:
            self.log.error('Error decoding auth.conf of request %s' % requestname)
            raise e

    def requestPairing(self, commonname):
        '''
        Create a request in the VC3 category to create a pairing setup protected by the supplied pairingcode.
        Master will see request, generate keypair, and place in infoservice w/ code. 
         
        '''
        code = self.ic.requestPairing(commonname)
        return code
        
    
    def getPairing(self, pairingcode):
        '''
        One-time only successful call. 
        Can be called unsuccessfully (i.e. during wait for request satisfaction) without harm. 
        Returns tuple of (pubsslkey, privsslkey)
         
        '''
        (cert, key) = self.ic.getPairing(pairingcode)
        return (cert, key)

##############################################
#          Private generic object methods.
#          To make code shorter.  
##############################################
    def _listEntities(self, entityclass ):
        m = sys.modules[__name__] 
        klass = getattr(m, entityclass)
        infokey = klass.infokey
        self.log.debug("Listing class %s with infokey %s " % (entityclass, infokey))     
        docobj = self.ic.getdocumentobject(infokey)
        self.log.debug("Got document object: %s " % docobj)
        olist = []
        try:
            for oname in docobj[infokey].keys():
                    self.log.debug("Getting objectname %s" % oname)
                    #s = "{ '%s' : %s }" % (oname, docobj[infokey][oname] )
                    nd = {}
                    nd[oname] = docobj[infokey][oname]
                    eo = klass.objectFromDict(nd)
                    self.log.debug("Appending eo %s" % eo)
                    olist.append(eo)
        except KeyError, e:
            self.log.warning("Document object does not have a '%s' key" % e.args[0])
        return olist


    def _getEntity(self, entityclass, objectname):
        eolist = self._listEntities(entityclass)
        self.log.debug("Got list of %d entity objects, matching entityclass %s..." % (len(eolist), 
                                                                                     entityclass))
        for eo in eolist:
            if eo.name == objectname:
                self.log.debug("Found object of correct name %s" % objectname)
                return eo
        self.log.debug("Didn't find desired objectname %s" % objectname)

##############################################
#        External Utility class methods. 
##############################################

    @classmethod
    def encode(self, string):
        return base64.b64encode(string)
    
    @classmethod
    def decode(self, string):
        return base64.b64decode(string)
        
    
class EntityExistsException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class MissingDependencyException(Exception):
    '''
    To be thrown when an API call includes a reference to an entity that doesn't exist. 
    '''
    def __init__(self, name, entityclass):
        self.name        = name
        self.entityclass = entityclass
    def __str__(self):
        return repr(self.name) + '(' + repr(self.entityclass) + ')'

