from six.moves import urllib
import os
import requests
import logging
from clarus.api_config import ApiConfig

#DIRECTORY    = 'c:/clarusft/data/test/'            # where to look for data files

logger = logging.getLogger(__name__)

def openFile(fileName, mode='r'):
    if (os.path.isfile(fileName)) :
        return open(fileName, mode)
    if os.path.isdir(ApiConfig.resource_path):
        fileName = ApiConfig.resource_path+fileName
    return open(fileName, mode)
        
def read(fileNames):
    if 'CHARM_RESOURCE_PATH' in os.environ:
        resourcePath = os.environ['CHARM_RESOURCE_PATH']
        return readResources(fileNames, resourcePath);
    else:
        return readFiles(fileNames);

def readFiles(fileNames):
    streams = []
    for fileName in fileNames.split(','):
        try:
            streams.append(openFile(fileName.strip()).read())
        except IOError as error:
            logger.error("Error can't open file " + fileName)
            raise error
    return streams;

def readResources(resourceNames, resourcePath):
    streams = []
    for resourceName in resourceNames.split(','):
        resource = readResource(resourceName, resourcePath)
        if resource is not None:
            streams.append(resource);
        else:
            raise IOError('Cannot open resource '+resourceName)
    return streams;

def readResource(resourceName, resourcePath):
    if resourcePath.startswith('http'):
        return readHttpResource(resourceName, resourcePath)
    else:
        return None

def readHttpResource(resourceName, resourcePath):
    url = resourcePath + urllib.parse.quote_plus(resourceName)
    logger.debug ('reading http resource '+url)
    r = requests.get(url)
    if r.status_code != 200:
        logger.error ('error reading http resource: '+str(r.status_code)+" " + r.text)
        return None
    else:
        return r.text

def write(fileName, data):
    try:
        f = openFile(fileName.strip(), 'w')
        f.write(data.text)
    except IOError as error:
        logger.error ("Error can't open file " + fileName);
        raise error