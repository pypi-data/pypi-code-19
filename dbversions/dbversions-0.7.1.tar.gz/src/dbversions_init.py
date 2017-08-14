#!/usr/bin/env python
'''
Created on 14. Okt. 2016

@author: chof
'''
import getopt, sys, os
import logging
import shutil
from dbversions import Config, getResourcePath, VERBOSITY

global logger

def usage():
    pass


def checkDatabasePath(dbpath):
#*******************************************************************************
    global logger    
    if not os.path.isdir(dbpath):
        logger.info('Create database directory at %s' % (dbpath))
        os.makedirs(dbpath)

def copyDBConfig(dbconfig):
#*******************************************************************************
    global logger    
    shutil.copyfile(getResourcePath('data/templates/dbconfig.json'), dbconfig)
    logger.debug('Initializing dbversions configuration in %s' % (dbconfig))

def copyDBVersionsConfFile(path):
#*******************************************************************************    
    global logger    
    Config.enableDBVersionConfig(path)
    logger.debug('Setting up control file .dbversions in %s' % (path))
    
def linkPostCheckoutHook(path):
#*******************************************************************************    
    global logger    
    hookscript = os.path.join(os.path.dirname(__file__), 
                       'dbversions_postcheckout.py')
    hooklink = os.path.join(path, '.git/hooks/post-checkout')
    
    if (os.path.exists(hookscript)):
        
        if (os.path.exists(hooklink)):
            logger.warn(('The git hook post-checkout already exists in the ' + 
                        'repository "%s".') 
                        % (path))
            logger.warn(('Please check and link manually to ' +
                        'link from \033[1;34m%s\033[0m') % (hookscript))
        else:
            logger.info('Link post-checkout hoot to %s' % (hookscript))
            os.link(hookscript, hooklink)
    else:
        logger.error('Could not find the script dbversions_postcheckout.py at %s!' 
                     % (hookscript))

def initRepository(path):
#*******************************************************************************
    global  logger    
    dbpath = os.path.join(path, 'database')
    dbconfig = os.path.join(dbpath, 'db-config.json')

    checkDatabasePath(dbpath)
    copyDBConfig(dbconfig)    
    copyDBVersionsConfFile(path)
    linkPostCheckoutHook(path)

if __name__ == '__main__':
    
    logging.basicConfig(format='[%(asctime)s | %(name)s | %(levelname)-5s]: %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    logger = logging.getLogger('dbversions')
    
    projectpath = '.'
    verbosity = 1
    
    try:
        command = sys.argv[1]
        optlist, args = getopt.getopt(sys.argv[1:], 'vp:', ["projectpath=", ])
        
        for option, value in optlist:
            if option in ["-p", "--projectpath"]:
                projectpath = value
            elif option in ['-v']:
                verbosity = verbosity + 1
            else:
                assert False, "%s is an unhandled option" % (option)    
    except getopt.GetoptError as e:
        print str(e)
        usage()

    verbosity = verbosity if verbosity<=3 else 3
    logger.setLevel(VERBOSITY[verbosity])
    initRepository(projectpath)