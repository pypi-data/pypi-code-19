'''
Created on 16. Sep. 2016

@author: chof
'''
import os, codecs
import subprocess
import logging
from subprocess import call, Popen
from dbversions import astring

class SQLExecutionError(Exception):
    pass

class DbDump(object):
    '''
    classdocs
    '''


    def __init__(self, config):
    #***************************************************************************
        '''
        Constructor
        '''
        self.cfg = config
        self.logger = logging.getLogger('phpdbgit')
        pass    
    
    def makealldumps(self, environment):
    #***************************************************************************
        dbs = self.cfg.databases(environment)
        for db in dbs:
            self.makedump(db)
            
    def makedump(self, database):
    #***************************************************************************
        
        out = self._getOutputName()
        commit = self.cfg.getHeadHash()
        if not os.path.isdir(out):
            self.cfg.logger.info("create new snapshot for %s" %(commit))
            os.makedirs(out)
        
        dumpparams = [
             'mysqldump', 
             '--databases', 
             '--routines', 
             '--add-drop-database', 
             '--add-drop-table']
        
        dumpparams.append(database)
        
        dumpfile = out + "/" + database + ".sql"
        
        self.cfg.logger.info("take snapshot %s for %s" % (database, commit))
        self.cfg.logger.debug("stored in %s" % (dumpfile)) 
        
        with open(dumpfile, 'w') as f:
            call(dumpparams, stdout = f)
        
    def restorealldumpsforcommit(self, commit, env):
    #***************************************************************************
        databases = self.cfg.databases(env)
        for database in databases:
            self.restoredump(database, commit)
        

    def restoredump(self, database, commit):
    #***************************************************************************
        dumpfile = self.cfg.outputpath + "/" + astring(commit) + "/" + database + ".sql" 
        
        self.cfg.logger.info("Restoring database %s from dump at commit %s" % 
                         (database, astring(commit)))
        self.cfg.logger.debug("restore file: %s" % (dumpfile))

        try:
            with open(dumpfile, 'r') as f:
                call(['mysql'], stdin = f)
        except IOError:
            self.cfg.logger.warn("No dump for %s stored in %s" % (database, commit))
            
    def getAllDumpHashs(self):
    #***************************************************************************
        names = []
        for name in [name for name in os.listdir(self.cfg.outputpath)
            if os.path.isdir(os.path.join(self.cfg.outputpath, name))] :
            if self.cfg.repo.commit(name) != None:
                names += [name]
                
        return names
    

    def _replaceDBVariables(self, script, environment, dbs):
    #***************************************************************************
        scripttext = ""
        with open(script, 'rt') as scriptin:
            for line in scriptin:
                line = unicode(line, "utf-8")
                for db in dbs:
                    database = self.cfg.getDBName(db, environment)
                    if (database != ""):
                        line = line.replace("{%s}" % (db), database)
                    else:
                        raise EnvironmentError("%s does not have an environment %s" % (db, environment))
                
                scripttext = scripttext + line
        
        return scripttext

    def executeScript(self, script, environment):
    #***************************************************************************
        scripttext = self._replaceDBVariables(script, environment, 
                                              self.cfg.databases(None))
        
        self.cfg.logger.info("Execute SQL script %s on %s" % (script, environment))
        try:
            self._execute(scripttext)
            return True
        except SQLExecutionError as err:
            self.cfg.logger.error("Error during execution of %s: %s" % (script, err))
            return False
        
    def prepareScriptFor(self, script, environment):
    #***************************************************************************
        scripttext = self._replaceDBVariables(script, environment, 
                                              self.cfg.databases(None))
        with codecs.open(script, encoding='utf-8',  mode='w') as scriptout:
            scriptout.write(scripttext)
            
        

    def _getOutputName(self):
    #***************************************************************************
        return self.cfg.outputpath + '/' + self.cfg.getHeadHash()
        
    def _execute(self, script):
    #***************************************************************************
        script = script.encode("utf-8")
        pid = Popen(['mysql'], stdin = subprocess.PIPE, stderr = subprocess.PIPE)
        out, err = pid.communicate(script)
        pid.wait()
        
        if (err):
            raise SQLExecutionError(err)
        else:
            return 0
          
        