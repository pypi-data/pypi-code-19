'''
Created on 15. Sep. 2016

@author: chof
'''

import json
import os

from git import Repo
from dbversions import astring, getResourcePath, VERBOSITY
import logging



class Config(object):
    '''
    classdocs
    
    The configuration class takes the project path to initialize the repo and
    also the configuration file for the database (db-config.json) as well as
    the dbversion basics (.dbversion) another json file which is kept seperately
    to enable sandbox specific locations of dump directory and files.
    
    db-config.json is project specific and should be versioned in git
    '''
    
    DBVERSION_CONFIG = '.dbversion'
        
    @staticmethod
    def enableDBVersionConfig(projectpath):
        dbconfigfile = projectpath + '/' + Config.DBVERSION_CONFIG
        if not os.path.isfile(dbconfigfile) :
            import shutil
            shutil.copyfile(getResourcePath('data/templates/dbversion-configfile.json'), 
                            dbconfigfile)
        
        return dbconfigfile
    
    def __init__(self, projectpath):
        '''
        Constructor
        '''
    #***************************************************************************
        self.repodir = projectpath
        parameters = self._readBaseConfig(projectpath)
        
        dbconfigfile = projectpath + "/" + astring(parameters['dbconfig'])
        
        with open (dbconfigfile) as config_file:
            self._dbconfig = json.load(config_file)
            
        self.repo = Repo(self.repodir)
        self.outputpath = self.fullpath(parameters['dumpspath'])        
        self.setupscriptpath = self.fullpath(self._dbconfig['setupscripts'])
        
        logging.basicConfig(format=parameters['logger']['logformat'],
                            datefmt=parameters['logger']['logdatefmt'])
        self.logger = logging.getLogger('dbversions')
        self.setLoggingVerbosity(parameters['logger']['default-verbosity'])
        self.environments = parameters['environments']
            
    def setLoggingVerbosity(self, verbosity):
    #***************************************************************************
        if verbosity > 3:
            verbosity = 3            
        
        self.logger.setLevel(VERBOSITY[verbosity])
        
    def fullpath(self, path):
    #***************************************************************************
        return "%s/%s" % (self.repodir, astring(path))
    
    def databases(self, environment):
    #***************************************************************************
        dbs = self._dbconfig['databases']
        dblist = []
        if not environment == None:
            for db in dbs:
                if (dbs[db].has_key(environment)):
                    dblist.append(astring(dbs[db][environment]))
                else:
                    self.logger.warn('Environment %s not available for database %s' 
                                     % (environment, db))
        else:
            for db in dbs:
                dblist.append(astring(db))
        
        return dblist
    
    def getDBName(self, db, env):
    #***************************************************************************
        dbname = ''
        dbs = self._dbconfig['databases']
        if dbs.has_key(db):
            if dbs[db].has_key(env):
                dbname = dbs[db][env]
                
        return dbname
    
    def getEnvironments(self):
        return self.environments
    
    def getHead(self):
    #***************************************************************************
        return self.repo.commit('HEAD')
    
    def getHeadOfBranch(self, branch):
        return self.repo.heads[branch]
    
    def getHeadHash(self):
    #***************************************************************************
        return astring(self.getHead().hexsha)
    
    def _readBaseConfig(self, projectpath):
    #***************************************************************************
        dbconfigfile = self.enableDBVersionConfig(projectpath)
        
        with open(dbconfigfile) as f:
            parameters = json.load(f)
        return parameters
            