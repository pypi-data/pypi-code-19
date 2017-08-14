#!/usr/bin/env python
'''
Created on 15. Sep. 2016

@author: chof
'''

from dbversions import Config, DbDump, DBConfig, parseEnvironments
from dbversions.gitanalyzer import ConflictingDBScripts
import getopt
import sys


def usage():
#***************************************************************************    
    pass

global environment
global cfg
global dbdumps

if __name__ == '__main__':
    environment = None
    projectpath = '.'
    verbosity = 0
    outputPath = '.'
    
    try:
        command = sys.argv[1]
        optlist, args = getopt.getopt(sys.argv[2:], 'vp:e:o:s:', ["projectpath=", "env=", "script=", "output="])
        
        for option, value in optlist:
            if option in ["-p", "--projectpath"]:
                projectpath = value
            elif option in ["-s", "--script"]:
                script = value 
            elif option in ["-o", "--output"]:
                outputPath = value
            elif option in ['-e', '--env']:
                environment = parseEnvironments(value)
            elif option in ['-v']:
                verbosity = verbosity + 1
            else:
                assert False, "%s is an unhandled option" % (option)    
    except getopt.GetoptError as e:
        print str(e)
        usage()

    cfg = Config(projectpath)
    
    if environment == None:
        environment = cfg.environments
    else:
        cfg.environments = environment
        
    if verbosity > 0 :
        cfg.setLoggingVerbosity(verbosity)
    
    dbconfig = DBConfig(cfg)
    dbdumps = DbDump(cfg)
    
    if (command == 'snapshot'):
        dbconfig.snapshot()
            
    elif (command == 'restore'):
        dbconfig.restore()

    elif (command == 'switch'):
        dbconfig.switch()
        
    elif (command == 'checkout'):
        dbconfig.checkout()
        
    elif (command == 'list'):
        dbconfig.list()
        
    elif(command == 'build'):
        dbconfig.build(outputPath)
        
    elif (command == 'merge'):
        main = cfg.getHeadOfBranch(args.pop(0))
        topic = cfg.getHeadOfBranch(args.pop(0))
        try:
            dbconfig.merge(main, topic)
        except ConflictingDBScripts as e:
            cfg.logger.error("Conflicting DB Scripts:")
            cfg.logger.error(e.pathA) 
            cfg.logger.error(e.pathB) 
        
    elif (command == 'execute'):
        try: 
            dbconfig.execute(script)
        except EnvironmentError as e:
            cfg.logger.error(e)


    pass