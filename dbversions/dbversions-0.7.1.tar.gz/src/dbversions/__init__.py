from git import Commit
import os,sys
import logging

def astring(s):
    
    if isinstance(s, unicode):
        s = s.encode('ascii', 'ignore')
    elif isinstance(s, Commit):
        s = s.hexsha
    return s

def getResourcePath(resource): 
    return os.path.join(os.path.dirname(sys.modules['dbversions'].__file__), 
                       resource)
    
VERBOSITY = [logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG]
        

from config import Config 
from db import DbDump
from gitanalyzer import GitAnalyzer
from DBConfig import DBConfig

def parseEnvironments(option):
    envs = option.split(',')
    return envs