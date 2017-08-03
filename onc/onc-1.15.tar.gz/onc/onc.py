#-------------------------------------------------------------------------------
# Name:        onc
# Purpose:     This class provides access to the Oceans 2.0 API
#
# Author:      ryanross
#
# Created:     31/10/2016
# Copyright:   (c) Ocean Networks Canada 2016
# Licence:     None
# Requires:    Python 3.5+ - https://www.python.org/downloads/release/python-360/
#              requests library - [Python Install]\scripts\pip install requests
#-------------------------------------------------------------------------------
import sys
import os
import requests
import json
import math
import time
from datetime import datetime
import errno
import os.path
from contextlib import closing
import threading
# import numpy

if sys.version_info.major == 2:
    from V2 import util
else:
    from onc.V3 import util
    

lock = threading.Lock()

class ONC:
    baseUrl = "http://qaweb2.neptune.uvic.ca/"
    token = None
    showInfo = False
    outPath = None
    
    filterMap = {'locationCode':'station',
                 'deviceCategoryCode':'deviceCategory',
#                  'propertyCode':'sensors',
                 'begin':'dateFrom',
                 'end':'dateTo',
                 'station':'locationCode',
                 'stationName':'locationCode',
                 'deviceCategory':'deviceCategoryCode',
#                  'sensors':'propertyCodes',
#                  'sensor':'propertyCode',
                 'dateFrom':'begin',
                 'dateTo':'end'}
            

    def __init__(self, token, production=True, showInfo=False, outPath='c:/temp'):
        self.token = token
        if production:
            self.baseUrl = "http://data.oceannetworks.ca/"
        else:
            self.baseUrl = "http://qaweb2.neptune.uvic.ca/"
        self.showInfo = showInfo
        self.outPath = outPath

        self.pyVersion = sys.version_info.major
        




    '''
    DISCOVERY Methods
    '''

    '''
    Method to print to the console, the Locations Hierarchy at and below a specific locationCode
    '''
    def printLocationsHierarchy(self, 
                              parameters={},
                              includeData=False):
        
        locationCodes = []
    
        url='{}api/locations'.format(self.baseUrl)
    
        parameters['method'] = 'getTree'
        parameters['token'] = self.token
        if(self.showInfo):
            fullURL = 'URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()])))
            print(fullURL)
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
        if (response.ok):
            if (self.showInfo):print('Locations')
            locations = json.loads(util.toString(response.content))
            for location in locations:
                locationCode = location['locationCode']
                locationName = location['locationName']
                hasDeviceData = location['hasDeviceData']
                hasPropertyData = location['hasPropertyData']
                children = location['children']
                print('{0} - {1}'.format(locationCode,locationName))
                
                if (includeData):
                    if (hasDeviceData=='true'):
                        print('  Device Categories (Site Devices):')
                        deviceCategories = self.getDeviceCategories({"locationCode":locationCode})
                        for dc in deviceCategories:
                            deviceCategoryCode = dc['deviceCategoryCode']
                            deviceCategoryName = dc['deviceCategoryName']
                            print('    {0} - {1}'.format(deviceCategoryCode,deviceCategoryName))
                            properties = self.getProperties({"locationCode":locationCode,"deviceCategoryCode":deviceCategoryCode})
                            for p in properties:
                                propertyCode = p['propertyCode']
                                propertyName = p['propertyName']
                                print('      {0} - {1}'.format(propertyCode,propertyName))
                            
                        
                    if (hasPropertyData=='true'):
                        print('  Properties (Primary Sensors):')
                        properties = self.getProperties({"locationCode":locationCode})
                        for p in properties:
                            propertyCode = p['propertyCode']
                            propertyName = p['propertyName']
                            prpData = p['hasPropertyData']
                            deviceData = p['hasDeviceData']
                            print('    {0} - {1} property={2},device={3}'.format(propertyCode,propertyName,prpData,deviceData))
                            
                
                if (children):
                    for child in children:
                        self.getLocationChild(child,2,includeData)   
        else:
            util.printErrorMesasge(response,parameters)
            return False
    
        if (self.showInfo): print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo): util.printResponseTime(end,start)
        
        return locationCodes
 
    '''
    Method to print to the console, the Locations Hierarchy at and below a specific locationCode
    '''
    def printLocationsHierarchySingleLine(self, 
                              parameters={},
                              includeData=False):
        
        locationCodes = []
    
        url='{}api/locations'.format(self.baseUrl)
    
        parameters['method'] = 'getTree'
        parameters['token'] = self.token
        if(self.showInfo):
            fullURL = 'URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()])))
            print(fullURL)
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
        if (response.ok):
            if (self.showInfo):print('Locations')
            locations = json.loads(util.toString(response.content))
            for location in locations:
                locationCode = location['locationCode']
                locationName = location['locationName']
                hasDeviceData = location['hasDeviceData']
                hasPropertyData = location['hasPropertyData']
                children = location['children']
                #print('{0} - {1}'.format(locationCode,locationName))
                
                if (includeData):
                    if (hasDeviceData=='true'):
                        print('  Device Categories (Site Devices):')
                        deviceCategories = self.getDeviceCategories({"locationCode":locationCode})
                        for dc in deviceCategories:
                            deviceCategoryCode = dc['deviceCategoryCode']
                            deviceCategoryName = dc['deviceCategoryName']
                            
                            properties = self.getProperties({"locationCode":locationCode,"deviceCategoryCode":deviceCategoryCode})
                            
                            sProperties = ','.join([p['propertyCode'] for p in properties])
                            print('{0} - {1};{2} - {3};{4}'.format(locationCode,locationName,deviceCategoryCode,deviceCategoryName,sProperties))
#                             for p in properties:
#                                 propertyCode = p['propertyCode']
#                                 propertyName = p['propertyName']
#                                 print('      {0} - {1}'.format(propertyCode,propertyName))
                            
                        
                    if (hasPropertyData=='true'):
#                         print('  Properties (Primary Sensors):')
                        properties = self.getProperties({"locationCode":locationCode})
                        sProperties = ','.join([p['propertyCode'] for p in properties])
                        print('{0} - {1};{2}'.format(locationCode,locationName,sProperties))
#                         for p in properties:
#                             propertyCode = p['propertyCode']
#                             propertyName = p['propertyName']
#                             prpData = p['hasPropertyData']
#                             deviceData = p['hasDeviceData']
#                             print('    {0} - {1} property={2},device={3}'.format(propertyCode,propertyName,prpData,deviceData))
                            
                
                if (children):
                    for child in children:
                        self.getLocationChildSingleLine(child,2,includeData)   
        else:
            util.printErrorMesasge(response,parameters)
            return False
    
        if (self.showInfo): print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo): util.printResponseTime(end,start)
        
        return locationCodes
       
    '''
    Method to return the child location of a location in the hierarchy
    '''
    def getLocationChild(self,location,level,includeData=False):
        locationCode = location['locationCode']
        locationName = location['locationName']
        hasDeviceData = location['hasDeviceData']
        hasPropertyData = location['hasPropertyData']
        children = location['children']
        sTab = "  ".join(["" for r in range(0,level)])
        print('{0}{1} - {2}'.format(sTab,locationCode,locationName))
        
     
        if (includeData):
            if (hasDeviceData=='true'):
                print('{0}  Device Categories (Site Devices):'.format(sTab))
                deviceCategories = self.getDeviceCategories({"locationCode":locationCode})
                for dc in deviceCategories:
                    deviceCategoryCode = dc['deviceCategoryCode']
                    deviceCategoryName = dc['deviceCategoryName']
                    print('{0}    {1} - {2}'.format(sTab,deviceCategoryCode,deviceCategoryName))
                    properties = self.getProperties({"locationCode":locationCode,"deviceCategoryCode":deviceCategoryCode})
                    for p in properties:
                        propertyCode = p['propertyCode']
                        propertyName = p['propertyName']
                        print('{0}      {1} - {2}'.format(sTab,propertyCode,propertyName))
                
            if (hasPropertyData=='true'):
                properties = self.getProperties({"locationCode":locationCode})
                print('{0}  Properties (Primary Sensors):'.format(sTab))
                for p in properties:
                    propertyCode = p['propertyCode']
                    propertyName = p['propertyName']
                    print('{0}    {1} - {2}'.format(sTab,propertyCode,propertyName))
            
        if (children):
            for child in children:
                self.getLocationChild(child,level+1,includeData)
 
 
    '''
    Method to return the child location of a location in the hierarchy
    '''
    def getLocationChildSingleLine(self,location,level,includeData=False):
        locationCode = location['locationCode']
        locationName = location['locationName']
        hasDeviceData = location['hasDeviceData']
        hasPropertyData = location['hasPropertyData']
        children = location['children']
        sTab = "  ".join(["" for r in range(0,level)])
#         print('{0}{1} - {2}'.format(sTab,locationCode,locationName))
        
     
        if (includeData):
            if (hasDeviceData=='true'):
#                 print('{0}  Device Categories (Site Devices):'.format(sTab))
                deviceCategories = self.getDeviceCategories({"locationCode":locationCode})
                for dc in deviceCategories:
                    deviceCategoryCode = dc['deviceCategoryCode']
                    deviceCategoryName = dc['deviceCategoryName']
#                     print('{0}    {1} - {2}'.format(sTab,deviceCategoryCode,deviceCategoryName))
                    properties = self.getProperties({"locationCode":locationCode,"deviceCategoryCode":deviceCategoryCode})
                    sProperties = ','.join([p['propertyCode'] for p in properties])
                    print('{0} - {1};{2} - {3};{4}'.format(locationCode,locationName,deviceCategoryCode,deviceCategoryName,sProperties))
#                     for p in properties:
#                         propertyCode = p['propertyCode']
#                         propertyName = p['propertyName']
#                         print('{0}      {1} - {2}'.format(sTab,propertyCode,propertyName))
                
            if (hasPropertyData=='true'):
                properties = self.getProperties({"locationCode":locationCode})
                sProperties = ','.join([p['propertyCode'] for p in properties])
                print('{0} - {1};{2}'.format(locationCode,locationName,sProperties))
#                 print('{0}  Properties (Primary Sensors):'.format(sTab))
#                 for p in properties:
#                     propertyCode = p['propertyCode']
#                     propertyName = p['propertyName']
#                     print('{0}    {1} - {2}'.format(sTab,propertyCode,propertyName))
            if ((hasDeviceData!='true') and (hasPropertyData!='true')):
                print('{0} - {1}'.format(locationCode,locationName))
                
        if (children):
            for child in children:
                self.getLocationChildSingleLine(child,level+1,includeData)
    
    '''
    Method to return a list of locations which match filter criteria defined by a dictionary of parameters
    '''
    def getLocations(self, 
                     parameters={}):
        
        locations = []
    
        url='{}api/locations'.format(self.baseUrl)
        parameters['method'] = 'get'
        parameters['token'] = self.token
        if(self.showInfo):
            fullURL = 'URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()])))
            print(fullURL)
    
        start = datetime.now()
        try:
            response = requests.get(url,params=parameters, verify=False)
        except Exception as e:
#             e = sys.exe_info()[0]
            print(e)
            
        end = datetime.now()
    
    
        if (response.ok):
            locations = json.loads(util.toString(response.content))
        else:
            util.printErrorMesasge(response,parameters)
    
        if (self.showInfo): print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo): util.printResponseTime(end,start)
        
        return locations
    
#     '''
#     Method to print the location codes and names to the console, which match filter criteria defined by a dictionary of parameters
#     '''
#     def printLocations(self, 
#                      parameters={}):
#         
#         print('Locations')
#         locations = self.getLocations(parameters)
#         for location in locations:
#             locationCode = location['locationCode']
#             locationName = location['locationName']
#             hasDeviceData = location['hasDeviceData']
#             hasPropertyData = location['hasPropertyData']
#             if (len(locationCode.split('.')) == 2):
#                 parentName = self.getLocationName(locationCode.split('.')[0])
#                 if (parentName):
#                     locationName = '{} / {}'.format(parentName,locationName)
# 
#             print('  {0} - {1}'.format(locationCode,locationName))
#             print('     Request data product using Device Category (Site Device): {}'.format(hasDeviceData))
#             print('     Request data product using Property (Primary Sensor): {}'.format(hasPropertyData))
# 
#         util.printCount(len(locations),'locations')

    '''
    Method to return a list of location codes which match filter criteria defined by a dictionary of parameters
    '''    
    def getLocationCodes(self, 
                     parameters={}):
        
        locations = self.getLocations(parameters)
        if not(locations=='False'):
            locationCodes = [l['locationCode'] for l in locations]
        
        return locationCodes
    
    '''
    Method to return a location name for a locationCode
    '''
    def getLocationName(self, 
                        locationCode):
        
        locationName = None
        
        parameters = {}
        parameters['method'] = 'get'
        parameters['token'] = self.token
        parameters['locationCode'] = locationCode
        
        locations = self.getLocations(parameters)

        if (len(locations) >= 1):
            locationNames = [l['locationName'] for l in locations if l['locationCode'] == locationCode]
            if len(locationNames) >=1:
                locationName = locationNames[0]
            
        return locationName
    
    '''
    Method to return a list of devices which match filter criteria defined by a dictionary of parameters
    '''
    def getDevices(self, 
                   parameters={}):
        
        devices = []
    
        url='{}api/devices'.format(self.baseUrl)
    
        parameters['method'] = 'get'
        parameters['token'] = self.token
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
    
        if (response.ok):
            if (self.showInfo):print('Devices')
            payload = response.content
            devices = json.loads(util.toString(payload))
        else:
            util.printErrorMesasge(response,parameters)
    
        if (self.showInfo):print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo):util.printResponseTime(end,start)
        
        return devices

#     '''
#     Method to print a list of devices to the console, which match filter criteria defined by a dictionary of parameters
#     '''
#     def printDevices(self, 
#                    parameters={}):
# 
#         print('Devices:')
# 
#         devices = self.getDevices(parameters)
#         for device in devices:
#             deviceCode = device['deviceCode']
#             deviceName = device['deviceName']
#             print('  {} - {}'.format(deviceCode,deviceName))
#         
#         util.printCount(len(devices),'devices')
        
    '''
    Method to return a list of device categories which match filter criteria defined by a dictionary of parameters
    '''
    def getDeviceCategories(self, 
                            parameters={}):
        
        deviceCategories = []
        url='{}api/deviceCategories'.format(self.baseUrl)
    
        parameters['method'] = 'get'
        parameters['token'] = self.token
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
        if (response.ok):
            payload = response.content
            deviceCategories = json.loads(util.toString(payload))
        else:
            util.printErrorMesasge(response,parameters)
    
        if (self.showInfo):print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo):util.printResponseTime(end,start)
        
        return deviceCategories
    
#     '''
#     Method to print a list of device categories to the console, which match filter criteria defined by a dictionary of parameters
#     '''
#     def printDeviceCategories(self, 
#                             parameters={}):
# 
#         deviceCategories = self.getDeviceCategories(parameters)
#         print('Device Categories:')
#         for deviceCategory in deviceCategories:
#             deviceCategoryCode = deviceCategory['deviceCategoryCode']
#             deviceCategoryName = deviceCategory['deviceCategoryName']
#             print('  {} - {}'.format(deviceCategoryCode,deviceCategoryName))
# 
#         util.printCount(len(deviceCategories),'device categories')


    '''
    Method to return a list of properties which match filter criteria defined by a dictionary of parameters
    '''
    def getProperties(self, 
                      parameters={}):
        
        properties = []
        url='{}api/properties'.format(self.baseUrl)
    
        parameters['method'] = 'get'
        parameters['token'] = self.token
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
        if (response.ok):
            if (self.showInfo):print('Properties')
            payload = response.content
            properties = json.loads(util.toString(payload))
    
        else:
            util.printErrorMesasge(response,parameters)
          
        return properties

#     '''
#     Method to print a list of properties to the console, which match filter criteria defined by a dictionary of parameters
#     '''
#     def printProperties(self, 
#                         parameters={}):
#         
#             properties = self.getProperties(parameters)
# 
#             for prprty in properties:
#                 propertyCode = prprty['propertyCode']
#                 propertyName = prprty['propertyName']
#                 description = prprty['description']
#                 print('  {} - {} ({})'.format(propertyCode,propertyName,description))
# 
#     
    '''
    Method to return a list of data products which match filter criteria defined by a dictionary of parameters
    '''
    def getDataProducts(self, 
                        parameters={}):
        
        dataProducts = []
        url='{}api/dataProducts'.format(self.baseUrl)
    
        parameters['method'] = 'get'
        parameters['token'] = self.token
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
    
        if (response.ok):
            if (self.showInfo):print('Data Products')
            payload = response.content
            dataProducts = json.loads(util.toString(payload))   
        else:
            util.printErrorMesasge(response,parameters)
    
        if (self.showInfo): print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if(self.showInfo): util.printResponseTime(end,start)
        
        return dataProducts
    
#     '''
#     Method to print a list of data products to the console, which match filter criteria defined by a dictionary of parameters
#     '''
#     def printDataProducts(self, 
#                           parameters={}):
#         
#         if (self.showInfo):print('Data Products')
# 
#         dataProducts = self.getDataProducts(parameters)
# 
#         for c in sorted(set([str(dp['dataProductCode']) for dp in dataProducts])):
#             name = [dp['dataProductName'] for dp in dataProducts if dp['dataProductCode'] == c][0]
#             print ('{} - {}'.format(c,name))
#             for e in sorted(set([dp['extension'] for dp in dataProducts if dp['dataProductCode'] == c])):
#                 print('  {}'.format(e))
#             
    

#         #if the service does not support filtering, this code will filter.
#         if (len(dataProducts)):
#             for dataProduct in dataProducts:
#                 dataProductCode = dataProduct['dataProductCode']
#                 dataProductName = dataProduct['dataProductName']
#                 dataProductFormatExtension = dataProduct['extension']
#                 helpDocument = dataProduct['helpDocument']
# 
#                 print('  {} ({}) - {}'.format(dataProductCode,dataProductName,dataProductFormatExtension))
# 
#         util.printCount(len(dataProducts),'Data Products')

 
    
    '''
    DATA PRODCUT DELIVERY Methods
    '''
                
    '''
    Method to order a data product which matches the filter criteria defined in the parameters dictionary
    
    Ordering a data product consists of the following steps:
    1) requesting a data product, which includes estimates for download size and time
    2) running a data product kicks off a process on the task machine to generate the data product
    3) downloading the data product. The process will continue to poll the web service to determine if the product is ready to download.
       if it is not ready, status messages will be provided. Once it is ready, it will download the data product to disk
    '''
    def orderDataProduct(self, 
                         parameters,                #dictionary of web service filter parameters 
                         maxRetries=100,            #The number of time to retry a service before it stops
                         downloadResultsOnly=False, #Indicates if files will be downloaded or if only the url to the file will be returned
                         includeMetadataFile=True): #Determines if the method should download the associated metadata file in addition to downloading data files

        stats = {'requestRequestTime':0,'runRequestTime':0,'queuingTime':0,'runningTime':0,'transferringTime':0,'downloadingTime':0}
        queuingTimes = []
        runningTimes = []
        transferringTimes = []
        downloadingTimes = []
        downloadResults = []
        
        start = datetime.now()
        dpRequest = self.requestDataProduct(parameters)
        stats['requestRequestTime'] = (datetime.now() - start).total_seconds()

        if (dpRequest):
            if 'dpRequestId' in dpRequest:
            
                requestId = dpRequest['dpRequestId']
                estimatedProcessingTime = 1
                
                if 'numFiles' in dpRequest.keys():
                    numFiles = dpRequest['numFiles']
                    showsFileCount = False #True
                else:
                    numFiles = 0 #Will not display countdown
                    showsFileCount = False
                    
                if not showsFileCount or (numFiles >= 1 and showsFileCount):
                    print('Request Id: {}'.format(requestId))
                    if 'fileSize' in dpRequest.keys():print('File Size: {}'.format(util.convertSize(dpRequest['fileSize'])))
                    if 'numFiles' in dpRequest.keys():print('File Count: {}'.format(numFiles))
                    if 'downloadTimes' in dpRequest.keys():
                        print('Estimated download time:')
                        for e in sorted(dpRequest['downloadTimes'].items(),key=lambda t: t[1]): print('  {} - {} sec'.format(e[0],'{:0.2f}'.format(e[1])))
                    if 'estimatedFileSize' in dpRequest.keys():
                        try:
                            estimatedFileSize = util.convertSize(float(dpRequest['estimatedFileSize']))
                        except:
                            estimatedFileSize = dpRequest['estimatedFileSize']
                        
                        print('Estimated File Size: {}'.format(estimatedFileSize))
                    if 'estimatedProcessingTime' in dpRequest.keys():
                        try:
                            estimatedProcessingTime = float(dpRequest['estimatedProcessingTime'])
                            print('Estimated Processing Time: {}'.format(util.getHMS(estimatedProcessingTime)))
                        except:
                            estimatedProcessingTime = 1
                            print('Estimated Processing Time: {}'.format(dpRequest['estimatedProcessingTime']))
                    
                    start = datetime.now()
                    ids = self.runDataProduct(requestId)
#                     print('------')
#                     print(ids)
#                     print('------')
                    stats['runRequestTime'] = (datetime.now() - start).total_seconds()
                    
                    if (ids):
                        for id in ids:
                            if id > 0:
                                downloadResults = self.downloadDataProduct(id,numFiles,estimatedProcessingTime,maxRetries,downloadResultsOnly,includeMetadataFile)
#                                 print('------')
#                                 print(downloadResults)
#                                 print('------')
                                for r in downloadResults:
                                    queuingTimes.append(r['queuingTime'])
                                    runningTimes.append(r['runningTime'])
                                    transferringTimes.append(r['transferringTime'])
                                    downloadingTimes.append(r['downloadingTime'])                
                    
                    
                    stats['queuingTime'] = sum(queuingTimes)
                    stats['runningTime'] = sum(runningTimes) 
                    stats['transferringTime'] = sum(transferringTimes)
                    stats['downloadingTime'] = sum(downloadingTimes)
                    
                    execTime = (datetime.now() - start).total_seconds()
                    print('Actual Processing/Download Time: {}'.format(util.getHMS(execTime)))
                
                else:
                    print('No Files to Download for Run ID: {}'.format(requestId))
            
            else:
                print(dpRequest) #If there is a valid payload but the the dpRequestId is not present, may indicate that there is a generic error message being returned in the payload
            
   
        return {'downloadResults':downloadResults,'stats':stats}
    
            
    '''
    Method to Request a data product using the dataProductDelivery service and provides request information
    so that the calling function can decide if should run the data product.
    The dictionary of information it returns includes a requestID, which is used to run the data product,
    and estimates of the expected download times and file sizes. 
    '''
    def requestDataProduct(self, 
                           parameters={},
                           returnError=False): #If True, the function will return the error from the payload, otherwise it prints the message
        
        requestInfo = None
        url='{}api/dataProductDelivery'.format(self.baseUrl)
        
        if not 'method' in parameters:
            parameters['method'] = 'request'
        if not 'token' in parameters:
            parameters['token'] = self.token
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
    
        if (response.ok):
            payload = response.content
            requestInfo = json.loads(util.toString(payload))
        else:
            msg = util.printErrorMesasge(response,parameters)
            
            ######## TODO, get the url for the data product from the dataProducts Service
            dps = self.getDataProducts({'dataProductCode':parameters['dataProductCode'],'extension':parameters['extension']})
            for dp in dps:
                print("For data product usage information for {} - '{}' & extension {}, see {}".format(dp['dataProductCode'], dp['dataProductName'],dp['extension'],dp['helpDocument']))
            if returnError: 
                requestInfo=msg
    
        if (self.showInfo): print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo): util.printResponseTime(end,start)
        
        return requestInfo
    
    '''
    Method to Run a data product request using the dataProductDelivery service with a Request Id and 
    return a list of Ids of the Runs it initiates.
    '''
    def runDataProduct(self, 
                       requestId):
        
        ids = None
        url='{}api/dataProductDelivery'.format(self.baseUrl)
        parameters = {}
        parameters['method'] = 'run'
        parameters['token'] = self.token
        parameters['dpRequestId'] = requestId
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
        if (response.ok):
            payload = response.content
            r = json.loads(util.toString(payload))
            
            ids = [run['dpRunId'] for run in r]

        else:
            util.printErrorMesasge(response,parameters)
    
    
        if (self.showInfo): print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo): util.printResponseTime(end,start)
        
        return ids
    
    '''
    Method to poll the dataProductDelivery service until data product generation task is complete and
    download all of the files or retrieve the file information (url, file and download status).
    '''
    def downloadDataProduct(self, 
                            runId,                      # The ID of the run process to download the files for. RunIds are returned from the dataProductDelivery run method
                            fileCount=0,                # The actual or estimated file count, which is returned from the dataProductDelivery request method
                            estimatedProcessingTime=1,  # The estimated processing time in seconds, which is used to determine how often to poll the web service. The estimated processing time is returned from the dataProductDelivery request method
                            maxRetries=100,             # Determines the maximum number of times the process will poll the service before it times out. The purpose of this property is to prevent hung processes on the Task server to hang this process.
                            downloadResultsOnly=False,  # Determines if files will be downloaded by the __downloadDataProductIndex__ method, or if it returns information about the files so that they can be downloaded later.
                            includeMetadataFile=False,  # Determines if the method should download the associated metadata file in addition to downloading data files
                            multiThreadMessages=False): # Determines how the method and called method should print messages to the console. If downloading data products in a multi-threaded pattern, messages written to the console can overlap and progress dots can be written out of context 
        
        downloadResults = []
        
        url='{}api/dataProductDelivery'.format(self.baseUrl)
        parameters = {}
        parameters['method'] = 'download'
        parameters['token'] = self.token
        parameters['dpRunId'] = runId
        
        if (multiThreadMessages):
            with lock:
                print('Downloading files for Run ID: {}'.format(runId))
        else:
            if (fileCount != 0):
                util.printWithEnd('Downloading {0} files for Run ID: {1}'.format(fileCount,runId))
            else:
                util.printWithEnd('Downloading files for Run ID: {}'.format(runId))
            

        downloadCount = 0
        totalFileSize = 0
        
        indx = 1    #Index Number of file to download. 
                    #Because the number of files are not known until the process is complete, 
                    #we try the next index until we get back a 404 status indicating that we are beyond the end of the array
        
        while True:
            parameters['index'] = indx
            dict = self.__downloadDataProductIndex__(runId,url,parameters,downloadResultsOnly,multiThreadMessages,indx,fileCount,estimatedProcessingTime,maxRetries)
            if (dict):
                downloadResults.append(dict)
                if dict['status'] == 'error':
                    break
                else:
                    if 'downloaded' in dict:
                        if (dict['downloaded']): 
                            downloadCount+=1
                    if 'size' in dict: 
                        totalFileSize+=dict['size']
                    indx+=1
            else:
                break
        
        if (includeMetadataFile):
            #download the Metadata file if it exists
            parameters['index'] = 'meta'
            dict = self.__downloadDataProductIndex__(runId,url,parameters,downloadResultsOnly,multiThreadMessages,'meta',1,1,maxRetries)
            if (dict):
                downloadResults.append(dict)
                if 'downloaded' in dict:
                    if (dict['downloaded']): downloadCount+=1
                if 'size' in dict: 
                    totalFileSize+=dict['size']
        
       
        if (not multiThreadMessages):
            print('  {} files ({}) downloaded'.format(downloadCount, util.convertSize(totalFileSize)))
        
        return downloadResults
    
    '''
    Private Method to download a data product for a runId and Index (file number or 'meta').
    '''
    def __downloadDataProductIndex__(self, 
                                 runId,                     # The ID of the run process to download the files for. RunIds are returned from the dataProductDelivery run method
                                 url,                       # The full URL of the dataProductDelivery service
                                 parameters,                # The http request parameters for method, token, runId and index
                                 downloadResultsOnly,       # Determines if files will be downloaded by the __downloadDataProductIndex__ method, or if it returns information about the files so that they can be downloaded later.
                                 multiThreadMessages,       # Determines how the method and called method should print messages to the console. If downloading data products in a multi-threaded pattern, messages written to the console can overlap and progress dots can be written out of context
                                 indx=1,                    # The index of the file to be downloaded. Data files have an index of 1 or higher. The Metadata has an index of 'meta'
                                 fileCount=1,               # The actual or estimated file count, which is returned from the dataProductDelivery request method
                                 estimatedProcessingTime=1, # The estimated processing time in seconds, which is used to determine how often to poll the web service. The estimated processing time is returned from the dataProductDelivery request method
                                 maxRetries=100):           # Determines the maximum number of times the process will poll the service before it times out. The purpose of this property is to prevent hung processes on the Task server to hang this process.
                     
        
        defaultSleepTime = 2
        
        requestUrl = '{}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()])))
        downloadResult = {"url":requestUrl}
        tryCount = 0
        requestCount = 0
        lastMessage = None
        if (estimatedProcessingTime > 1):
            sleepTime = estimatedProcessingTime * 0.5
        else:
            sleepTime = defaultSleepTime
        downloadResult['message'] = []
        
        startQueuing = None
        endQueuing = None
        downloadResult['queuingTime'] = 0
        startRunning = None
        endRunning = None
        downloadResult['runningTime'] = 0
        startTransferring = None
        endTransferring = None
        downloadResult['transferringTime'] = 0
        startDownloading = None
        endDownloading = None
        downloadResult['downloadingTime'] = 0
        
        downloadResult['requestCount'] = 0
        
        while True:
            requestCount+=1
            tryCount+=1
            downloadResult['status'] = 'running'
            if tryCount >= maxRetries:
                msg = 'Maximum number of retries ({}) exceeded'.format(maxRetries)
                if multiThreadMessages: 
                    with lock:
                        print('{}: {}'.format(runId,msg))
                else:
                    print(msg)
                    
                downloadResult['message'].append(msg)
                break
            startDownloading = datetime.now()
            with closing(requests.get(url,params=parameters,stream=True)) as streamResponse:
                if (streamResponse.ok): #Indicates that the request was successful and did not fail. The status code indicates if the stream contains a file (200) or 
                    if streamResponse.status_code == 200: #OK
                        if (not endRunning):
                            endRunning = datetime.now()
                        if (startTransferring):
                            endTransferring = datetime.now()
                        tryCount=0                      
                        
                        if 'Content-Disposition' in streamResponse.headers.keys():
                            content = streamResponse.headers['Content-Disposition']
                            filename = content.split('filename=')[1]
                        else:
                            if (not multiThreadMessages): 
                                print('Error: Invalid Header')
                            streamResponse.close()
                            break
                        
                        if 'Content-Length' in streamResponse.headers.keys():
                            size = streamResponse.headers['Content-Length']
                            downloadResult['size'] = float(size)
                        else: 
                            size = 0
 
                        filePath = '{}/{}'.format(self.outPath,filename)
                        downloadResult['file'] = filePath
                        downloadResult['index'] = indx
                        
                        if downloadResultsOnly:
                            if (not multiThreadMessages): 
                                print('')
                                print("  download URL: {0}".format(requestUrl)) 
                            downloadResult['downloaded'] = False
                            downloadResult['status'] = 'complete'
                        else:
                            
                            try:
                                if (indx==1):
                                    if (not multiThreadMessages):
                                        print('')
                                
                                if (not os.path.isfile(filePath)):
                                    #Create the directory structure if it doesn't already exist
                                    try:
                                        os.makedirs(self.outPath)
                                    except OSError as exc:
                                        if exc.errno == errno.EEXIST and os.path.isdir(self.outPath):
                                            pass
                                        else:
                                            raise  
                                    
                                    if (not multiThreadMessages):
                                        if fileCount == 0:
                                            print ("  Downloading {} '{}' ({})".format(indx,filename,util.convertSize(float(size))))
                                        else:
                                            print ("  Downloading {}/{} '{}' ({})".format(indx,fileCount,filename,util.convertSize(float(size))))
                                        
                                    with open(filePath,'wb') as handle:
                                        try:
                                            for block in streamResponse.iter_content(1024):
                                                handle.write(block)
                                        except KeyboardInterrupt:
                                            if multiThreadMessages:
                                                print('{}: Process interupted: Deleting {}'.format(runId,filePath))
                                            else:
                                                print('Process interupted: Deleting {}'.format(filePath))
                                            handle.close()
                                            streamResponse.close()
                                            os.remove(filePath)
                                            sys.exit(-1)
                                else:
                                    if multiThreadMessages:
                                        print ("{}: {} Skipping '{}': File Already Exists".format(runId,indx,filename))
                                    else:
                                        if fileCount == 0:
                                            print ("  Skipping {} '{}': File Already Exists".format(indx,filename))
                                        else:
                                            print ("  Skipping {}/{} '{}': File Already Exists".format(indx,fileCount,filename))
                                
                                downloadResult['downloadingTime'] = (datetime.now() - startDownloading).total_seconds()
                                downloadResult['downloaded'] = True
                                downloadResult['status'] = 'complete'
                            except:
                                msg = 'Error streaming response.'
                                if multiThreadMessages: 
                                    with lock:
                                        print('{}: {}'.format(runId,msg))
                                else:
                                    print(msg)
                                    
                                downloadResult['message'].append(msg)
                                downloadResult['status'] = 'error'
                                
                        streamResponse.close()
                        break
                    elif streamResponse.status_code == 202: #Accepted - Result is not complete -> Retry
                        payload = json.loads(util.toString(streamResponse.content))
                        if len(payload) >= 1:
                            if 'message' in payload:
                                msg = payload['message']
                            elif 'status' in payload:
                                msg = payload['status']
                            else:
                                print('Error payload: {}'.format(payload))
                                break
                                
                            if ('Transferring' in msg and not startTransferring):
                                startTransferring = datetime.now()
                                if (not endRunning):
                                    endRunning = datetime.now()
                            
                            if (msg != lastMessage): #display a new message if it has changed
                                if multiThreadMessages: 
                                    with lock:
                                        print('{}: {}'.format(runId,msg))
                                else:
                                    util.printWithEnd('\n  {}'.format(msg))
                                    sys.stdout.flush()
                                    
                                downloadResult['message'].append(msg)
                                lastMessage=msg
                                tryCount=0
                                
                                if ('Queued' in msg):
                                    if (not startQueuing):
                                        startQueuing = datetime.now()
                                else:
                                    if (not startRunning):
                                        startRunning = datetime.now()
                                    
                                    if (startQueuing and not endQueuing):
                                        endQueuing = datetime.now()
                                    
                                
                            else: #Add a dot to the end of the message to indicate that it is still receiving the same message
                                if (not multiThreadMessages): 
                                    util.printWithEnd('.')
                                    sys.stdout.flush()
                                
                                
                        else:  
                            if (not multiThreadMessages):
                                print('Retrying...') 

                    elif streamResponse.status_code == 204: #No Content - No Data found
                        if not(util.toString(streamResponse.content) == ''):
                            payload = json.loads(util.toString(streamResponse.content))
                            msg = '  {} [{}]'.format(payload['message'],streamResponse.status_code)
                        else:
                            msg = 'No Data found'
                        
                        if multiThreadMessages:
                            with lock:
                                print('{}: {}'.format(runId,msg))
                        else:
                            print('\n{}'.format(msg))
                            
                        streamResponse.close()
                        
                        downloadResult['message'].append(msg)
                        downloadResult['status'] = 'complete'
                        endRunning = datetime.now()

                        break          
                    else:
                        msg = 'HTTP Status: {}'.format(streamResponse.status_code)
                        if multiThreadMessages:
                            with lock:
                                print('{}: {}'.format(runId,msg)) 
                        else:
                            print(msg)
                    
                        downloadResult['message'].append(msg)
                        endRunning = datetime.now()
                
                elif streamResponse.status_code == 400: #Error occurred
                    endRunning = datetime.now()
                    if startQueuing and (not endQueuing):
                        endQueuing = datetime.now()
                        
                    if (self.showInfo): print('  HTTP Status: {}'.format(streamResponse.status_code))
                    payload = json.loads(util.toString(streamResponse.content))
                    if len(payload) >= 1:                        
                        if ('errors' in payload):
                            for e in payload['errors']:
                                msg = e['errorMessage']    
                                util.printErrorMesasge(streamResponse,parameters)
                        elif ('message' in payload):
                            msg = '  {} [{}]'.format(payload['message'],streamResponse.status_code)
                            if (not multiThreadMessages):
                                print('\n{}'.format(msg))
                        else:
                            msg = 'Error occurred processing data product request'
                            if multiThreadMessages:
                                with lock:
                                    print('{}: {}'.format(runId,msg))
                            else:
                                print(msg)
                    else:
                        msg = 'Error occurred processing data product request'
                        if multiThreadMessages:
                            with lock:
                                print('{}: {}'.format(runId,msg))
                        else:
                            print(msg)

                    streamResponse.close()
                    downloadResult['status'] = 'error'
                    downloadResult['message'].append(msg)
                    break
                    
                elif streamResponse.status_code == 404:  #Not Found - Beyond End of Index - Index # > Results Count
                    streamResponse.close()
                    downloadResult = None
                    break
                
                elif streamResponse.status_code == 410: #Gone - file does not exist on the FTP server. It may not have been transfered to the FTP server  yet

                    
                    payload = json.loads(util.toString(streamResponse.content))
                    if len(payload) >= 1:
                        msg = payload['message']
                        if (msg != lastMessage):
                            
                            if multiThreadMessages:
                                with lock:
                                    print('{}: Waiting... {}'.format(runId,msg))
                            else:
                                util.printWithEnd('\n  Waiting... {}'.format(msg))
                                sys.stdout.flush()
                            
                            downloadResult['message'].append(msg)
                            lastMessage=msg
                            tryCount=0
                        else: 
                            if (not multiThreadMessages): 
                                util.printWithEnd('.','')
                                sys.stdout.flush()
                    else:
                        if multiThreadMessages:
                            with lock:
                                print('{}: Running... Writing File'.format(runId))
                        else:
                            print('\nRunning... Writing File.')
                            
                elif streamResponse.status_code == 500: #Internal Server Error occurred
                    print('')
                    msg = util.printErrorMesasge(streamResponse,parameters)
                    if (self.showInfo): print('  URL: {}'.format(streamResponse.url))
                    streamResponse.close()
                    downloadResult['status'] = 'error'
                    downloadResult['message'].append(msg)
                    break
                else:
                    try:
                        payload = json.loads(util.toString(streamResponse.content))
                        if len(payload) >= 1:
                            if ('errors' in payload):
                                for e in payload['errors']:
                                    msg = e['errorMessage']    
                                    util.printErrorMesasge(streamResponse,parameters)
                            elif ('message' in payload):
                                msg = payload['message']
                                if multiThreadMessages:
                                    with lock:
                                        print('{}: {} [{}]'.format(runId,msg,streamResponse.status_code))
                                else:
                                    print('\n  {} [{}]'.format(msg,streamResponse.status_code))
                            
                            downloadResult['status'] = 'error'
                            downloadResult['message'].append(msg)
                        streamResponse.close()
                        break 
                    except:
                        util.printErrorMesasge(streamResponse,parameters)
                        if multiThreadMessages:
                            with lock:
                                print('{}: {} Retrying...'.format(runId,msg))
                        else:
                            print('{} Retrying...'.format(msg))
                            
                        streamResponse.close()
                        break
                    
            streamResponse.close()
                      
            if (tryCount <= 5) and (sleepTime > defaultSleepTime):
                sleepTime = sleepTime * 0.5

            time.sleep(sleepTime)
            
        if (startQueuing and endQueuing):
            downloadResult['queuingTime'] = (endQueuing - startQueuing).total_seconds()
            
        if (startRunning and endRunning):
            downloadResult['runningTime'] = (endRunning - startRunning).total_seconds()

        if (startTransferring and endTransferring):
            downloadResult['transferringTime'] = (endTransferring - startTransferring).total_seconds()
        
        try:
            downloadResult['requestCount'] = requestCount
        except:
            ''''''
        
        return downloadResult

    '''
    Method to download a file from a URL, write it to a file and return download results information (url, file, message and download status).
    '''
    def downloadFile(self,
                    url,                        # The url to be downloaded
                    file,                       # The full path of the file to be downloaded to.
                    multiThreadMessages=False): # Determines how the method should print messages to the console. If downloading files in a multi-threaded pattern, messages written to the console can overlap and progress dots can be written out of context
        
        start = datetime.now()
                
        path = os.path.dirname(file)   
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(self.outPath):
                pass
            else:
                raise
        downloadResult = {"url":url,"file":file, 'message':[]}

        with closing(requests.get(url,stream=True)) as streamResponse:
            if (streamResponse.ok): #Indicates that the request was successful and did not fail. The status code indicates if the stream contains a file (200) or 
                if streamResponse.status_code == 200: #OK                   
                    try:
                        if (not os.path.isfile(file)):
                            with open(file,'wb') as handle:
                                try:
                                    for block in streamResponse.iter_content(1024):
                                        handle.write(block)
                                except KeyboardInterrupt:
                                    print('Process interupted: Deleting {}'.format(file))

                                    handle.close()
                                    streamResponse.close()
                                    os.remove(filePath)
                                    sys.exit(-1)
                        else:
                            msg = "Skipping '{}': File Already Exists".format(file)
                            if (multiThreadMessages):
                                with lock:
                                    print("{} for download '{}'".format(msg,url))
                            else:
                                print ("  {}".format(msg))
                            downloadResult['message'].append(msg)

                        downloadResult['downloaded'] = True
                        downloadResult['downloadingTime'] = (datetime.now() - start).total_seconds()
                    except:
                        msg = 'Error streaming response.'
                        if (multiThreadMessages):
                            with lock:
                                print("{} for download '{}'".format(msg,url))
                        else:
                            print(msg)
                        downloadResult['message'].append(msg)
                        downloadResult['downloaded'] = False
                            
                    streamResponse.close()
                else:
                    msg = 'HTTP Status: {}'.format(streamResponse.status_code)
                    if (multiThreadMessages):
                        with lock:
                            print("{} for download '{}'".format(msg,url))
                    else:
                        print(msg)
                    downloadResult['message'].append(msg)
                    downloadResult['downloaded'] = False
            else:
                try:
                    payload = json.loads(util.toString(streamResponse.content))
                    if len(payload) >= 1:
                        if ('errors' in payload):
                            for e in payload['errors']:
                                msg = e['errorMessage']    
                                util.printErrorMesasge(streamResponse,parameters)
                        elif ('message' in payload):
                            msg = payload['message']
                            if (multiThreadMessages):
                                with lock:
                                    print("{} [{}] for download '{}'".format(msg,streamResponse.status_code,url))
                            else:
                                print('\n  {} [{}]'.format(msg,streamResponse.status_code))
                            
                        downloadResult['message'].append(msg)
                    streamResponse.close()
                except:
                    msg = util.printErrorMesasge(streamResponse,parameters)
                    downloadResult['message'] = msg
                    streamResponse.close()
                
                downloadResult['downloaded'] = False

        
        return downloadResult

        
    
    '''
    Method to order a data product and return only the urls, for download at a later time.
    '''
    def getDataProductUrls(self, 
                           parameters, 
                           maxRetries=100):
        results = self.orderDataProduct(parameters, maxRetries, True)
        return [r['url'] for r in results['downloadResults'] if 'url' in r]
    
    
        '''
    Method to return a dictionary from the json response of a json data product download url.
    '''
    def decodeJsonFromUrl(self,url):
        
        jsonDataProduct = None
        
        start = datetime.now()
        response = requests.get(url)
        end = datetime.now()
    
    
        if (response.ok):
            payload = response.content
            try:
                jsonDataProduct = json.loads(util.toString(payload))
            except:
                print("Error - Response is not valid JSON")
        else:
            util.printErrorMesasge(response,{})
        
        return jsonDataProduct
    

    ''' 
    Near Real-Time methods 
    '''
    

    '''
    Method to return scalar data from the scalardata service in JSON Object format
    which match filter criteria defined by a dictionary of parameters.
    
    see https://wiki.oceannetworks.ca/display/help/scalardata+service for usage and available parameters
    '''    
    def getDirectScalar(self, 
                        parameters={},          #dictionary of web service filter parameters
                        outputFormat='Object',  #the response encoding is either Object (Data is a list of dictionaries with sampleTime, value and qaqcFlag for a given sensor) or Array (Data has 3 arrays for a given sensor. Array of sampleTime, array of values and array of qaqcFlags)
                        metadata='Full',        #The amount of metadata that is returned is either Full (default) and Minimum.
                        rowLimit=None):         #

        payload = {}
        
        url='{}api/scalardata'.format(self.baseUrl)
        
        parameters = self.__remapKeys__(parameters)
        parameters['method'] = "getByStation"
        parameters['token'] = self.token
        
        if (outputFormat in ['Object','Array']):
            parameters['outputFormat'] = outputFormat
        if (metadata in ['Minimum','Full']):
            parameters['metadata'] = metadata
        if rowLimit:
            parameters['rowLimit']=rowLimit
        
        
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
        
        sensorNames=[]
    
        if (response.ok):
            payload = json.loads(util.toString(response.content))
    
        else:
            util.printErrorMesasge(response,parameters)
    

        
        #update the metadata dictionary keys to the new filter names
        if ('serviceMetadata' in payload):
            payload['serviceMetadata'] = self.__remapKeys__(payload['serviceMetadata'])
        
        if ('metadata' in payload):
            payload['metadata'] = self.__remapKeys__(payload['metadata'])
        
        if ('sensorData' in payload and payload['sensorData']):
            l = []
            for d in payload['sensorData']:
                d = self.__remapKeys__(d)
                l.append(d)
            
            payload['sensorData'] = l
        
        
        if (self.showInfo):print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo):util.printResponseTime(end,start)
        
        return payload

    
                                        
    '''
    Method to return raw data from an instrument, in the payload, in JSON format from the rawdata service 
    which match filter criteria defined by a dictionary of parameters
    
    see https://wiki.oceannetworks.ca/display/help/rawdata+service for usage and available parameters
    '''   
    def getDirectRaw(self, 
                     parameters={}, #dictionary of web service filter parameters
                     rowLimit=None): #maximum number of rows of raw data that is returned. Default is 100,000
        
        payload = {}
        
        url='{}api/rawdata'.format(self.baseUrl)
        
        parameters = self.__remapKeys__(parameters)
        parameters['method'] = "getByStation"
        parameters['token'] = self.token
        if rowLimit:
            parameters['rowLimit']=rowLimit
    
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
        if (response.ok):
            payload = json.loads(util.toString(response.content))
    
        else:
            util.printErrorMesasge(response,parameters)
            return False
        
        if ('metadata' in payload):
            metadata = payload['metadata']
            if ('queryMetadata' in metadata):
                metadata['queryMetadata'] = self.__remapKeys__(metadata['queryMetadata'])
            
            if ('dataMetadata' in metadata):
                metadata['dataMetadata'] = self.__remapKeys__(metadata['dataMetadata'])
                
            payload['metadata'] = metadata
        
        if (self.showInfo):print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo):util.printResponseTime(end,start)
        
        return payload

    
    '''
    Method to download files from the archivefiles service 
    which match filter criteria defined by a dictionary of parameters
    
    see https://wiki.oceannetworks.ca/display/help/archivefiles for usage and available parameters
    '''
    def getDirectFiles(self, 
                       parameters={}):
        
        files = []
 
#         for key in parameters.keys():
#             if (key in self.filterMap.keys()):
#                 parameters[self.filterMap[key]] = parameters[key]
#                 del parameters[key]
        
        url='{}api/archivefiles'.format(self.baseUrl)
        parameters = self.__remapKeys__(parameters)
        parameters['method'] = "getList"
        parameters['token'] = self.token
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
        if self.showInfo: print(response.url)
        extension = None
        if ('extension' in parameters):
            extension = parameters['extension']
    
        if (response.ok):
            startDownload = datetime.now()
            print('Files')
            payload = json.loads(util.toString(response.content))
            totalFileSize = 0
            if (extension):
                fileCount = len([p for p in payload if p['filename'][-len(extension):]==extension])
            else:
                fileCount = len(payload)
            i = 1
            iDownloaded = 0
    
            for f in payload:
                filename = f['filename']
                filesize = f['uncompressedFileSize']
                dateFrom = f['dateFrom']
                dateTo = f['dateTo']
                
                if (extension): #Unable to filter by extension on the service call. We have to bring back all filenames and download only those files that match the extension passed in.
                    lstFilename =filename.split('.')
                    if (lstFilename[len(lstFilename)-1] != extension):
                        continue
    
                filePath = '{}/{}'.format(self.outPath,filename)
                if (not os.path.isfile(filePath)):
                    #Create the directory structure if it doesn't already exist
                    try:
                        os.makedirs(self.outPath)
                    except OSError as exc:
                        if exc.errno == errno.EEXIST and os.path.isdir(self.outPath):
                            pass
                        else:
                            raise  
                    
                    totalFileSize += filesize
                    print ("  Downloading {}/{} '{}' ({}) - {} to {}".format(i,fileCount,filename,util.convertSize(filesize),dateFrom,dateTo))
                    downloadParameters = {'method':'getFile','token':self.token,'filename':filename}
                    with open(filePath,'wb') as handle:
                        with closing(requests.get(url,params=downloadParameters,stream=True)) as streamResponse:
                            if (streamResponse.ok):
                                try:
                                    for block in streamResponse.iter_content(1024):
                                        handle.write(block)
                                except KeyboardInterrupt:
                                    print ('Process interupted: Deleting {}'.format(filePath))
                                    handle.close()
                                    streamResponse.close()
                                    os.remove(filePath)
                                    sys.exit(-1)
                            iDownloaded+=1
                else:
                    print ("  Skipping {}/{} '{}': File Already Exists".format(i,fileCount,filename))
    
                    
                i+=1
                files.append(filePath)
    
            endDownload = datetime.now()
    
    
            delta = endDownload - startDownload
            execTime = delta.seconds + delta.microseconds/1E6
    
            print('  {} files ({}) downloaded'.format(iDownloaded, util.convertSize(totalFileSize)))
            if (self.showInfo):util.printResponseTime(end,start)
            print('Total Download Time: {} seconds'.format(execTime))
        else:
            util.printErrorMesasge(response,parameters)
            return False
    
        if (self.showInfo):print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        if (self.showInfo):util.printResponseTime(end,start)
        
        return files
    

    '''
    Method to return scalar data observations using the scalardata service in array structure
    '''
    def getScalarObservations(self, 
                              parameters={}):
                                          
        observations = []
        payload = self.getDirectScalar(parameters,'Array')
        sensorData = payload['sensorData']
        
        sensorCount = len(sensorData)
        
        totalObservations = max([s['actualSamples'] for s in sensorData])
        
        for o in range(0,totalObservations):
            observation = {}
            for i in range(0,sensorCount):
                observation[sensorData[i]['sensor']] = sensorData[i]['data']['values'][o]
                if 'qaqcFlags' in sensorData[i]['data']:
                    observation['{}_qaqc'.format(sensorData[i]['sensor'])] = sensorData[i]['data']['qaqcFlags'][o]
            
            observation['sampleTime'] = sensorData[0]['data']['sampleTimes'][o]
            observations.append(observation)
            
        return observations

    '''
    Method to return resampled scalar data observations using the scalardata service in array structure
    '''
    def getScalarObservationsResample(self, 
                              parameters={},
                              resample='average'):
                                          
        payload = self.getDirectScalar(parameters,'Array')
        sensorData = payload['sensorData']
  
        sensorCount = len(sensorData)

        observation = {}
        for i in range(0,sensorCount):
            if resample=='average':
                val = numpy.average(sensorData[i]['data']['values'])
            elif resample=='mean':
                val = numpy.mean(sensorData[i]['data']['values'])
            elif resample=='median':
                val = numpy.median(sensorData[i]['data']['values'])
            elif resample=='min':
                val = min(sensorData[i]['data']['values'])
            elif resample=='max':
                val = max(sensorData[i]['data']['values'])
            else:
                val = None
                
            observation[sensorData[i]['sensor']] = val
        
        lstTime = [datetime.strptime(s.rstrip('Z'), '%Y-%m-%dT%H:%M:%S.%f') for s in sensorData[0]['data']['sampleTimes']]
        if resample=='median':
            dt = lstTime[int(len(lstTime)/2)]
        elif resample=='min':
            dt = min(lstTime)
        elif resample=='max':
            dt = max(lstTime)
        else:
            dt = (min(lstTime) + (((max(lstTime) - min(lstTime))) /2))
        
        observation['sampleTime'] = dt.strftime('%Y-%m-%dT%H:%M:%S.%f')+'Z'
        

        return observation        
        
    """
    Method to create a JSON file on disk from the scalardata service
    which match filter criteria defined by a dictionary of parameters.
    
    see https://wiki.oceannetworks.ca/display/help/scalardata+service for usage and available parameters
    """
    def writeDirectScalarToFile(self, 
                                parameters={}): #dictionary of web service filter parameters
        
        observations = []
        url='{api/}scalardata'.format(self.baseUrl)
    
        parameters['method'] = "getByStation"
        parameters['token'] = self.token
    
        print('Location')
        locationCode = parameters['station']
        self.getLocations({'locationCode': locationCode})
        print('Device Category')
        deviceCategoryCode = parameters['deviceCategory']
        self.getDeviceCategories({'deviceCategoryCode':deviceCategoryCode})
        if ('dateFrom' in parameters.keys()):
            print('From Date')
            print('  {}'.format(parameters['dateFrom']))
    
        if ('dateTo' in parameters.keys()):
            print('To Date')
            print('  {}'.format(parameters['dateTo']))
    
        outputFile ='{}/{}_{}.json'.format(self.outPath,locationCode,deviceCategoryCode)
        with open(outputFile,'wb') as handle:
            streamResponse = requests.get(url,params=parameters,stream=True)
    
            if (streamResponse.ok):
                for block in streamResponse.iter_content(1024):
                    handle.write(block)
                    
        print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))


    '''
    Method to return a list of observations from the SensorDataService
    which match filter criteria defined by a dictionary of parameters
    '''    
    def _getSensorData_(self, 
                        parameters={}):
    
        observations = []
        url='{}SensorDataService'.format(self.baseUrl)

        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
    
        if (response.ok):
    
            print('Sensor Data')
            payload = json.loads(util.toString(response.content))
    
            data = payload['payload']
            if (data):
                sdl = data['sensorDataList']
                if (sdl):
                     for d in sdl:
                        if d['statusCode'] < 0: print(d['message'])
    
                        metadata = d['sensorMetadata']
                        if (metadata):
                            print ("{} - {}".format(metadata['deviceName'],metadata['sensorName']))
    
    
                        readingList = d['sensorReadingDataList']
                        if (readingList):
                            for reading in readingList:
                                dicCol = {'value':reading['value'],'sampleTime':reading['sampleTime'],'qaqcFlag':reading['qaqcFlag']}
                                observations.append(dicCol)
    
    
        else:
            util.printErrorMesasge(response,parameters)
            return False
        print(' count: {}'.format(len(observations)))

        print('')
        if (self.showInfo):util.printResponseTime(end,start)
        
        return observations
    

    
    """
    Method to return scalar data in the payload, in JSON format 
    from the scalardata service and captures and returns performance statistics
    which match filter criteria defined by a dictionary of parameters.
    
    The purpose of this function is to test performance of the scalardata service
    for comparison with a dataProductDelivery service for the download of identical data.
    
    see https://wiki.oceannetworks.ca/display/help/scalardata+service for usage and available parameters
    """
    def _getScalarPerformance_(self, 
                             parameters={}, #dictionary of web service filter parameters
                             requestCount=10): #Number of times to repeat the same request for averaging
        stats = {}
        url='{}api/scalardata'.format(self.baseUrl)
    
        parameters['method'] = "getByStation"
        parameters['token'] = self.token
        parameters['outputFormat'] = 'Object' #Options Object or Array
        
        requestUrl = None
        responseTimes = []
        properties = []
        rowCount = None
        
        for i in range(requestCount):
            start = datetime.now()
            response = requests.get(url,params=parameters)
            end = datetime.now()
            delta = end - start
            execTime = delta.seconds + delta.microseconds/1E6
            
            if (response.ok):
                responseTimes.append(execTime)
                if self.showInfo:print("{}: {} sec".format(i+1,round(execTime,2)))
                if i==0:
                    requestUrl = response.url
                    payload = json.loads(util.toString(response.content))
            
                    if (payload):
                        sensorData = payload['sensorData']
                        if sensorData:
                            properties = [s['sensor'] for s in sensorData]
                        else:
                            print('No records found for {}'.format(parameters))
                        
                        serviceMetadata = payload['serviceMetadata']
                        if serviceMetadata:
                            sampleCount = serviceMetadata['totalActualSamples']
            else:
                print('Error {} - {} : {}'.format(response.status_code,response.reason,response.url))
                break
                        
        
        if (len(responseTimes) > 0):
            datetimeFormat = '%Y-%m-%dT%H:%M:%S.%fZ' 
            dtFrom = datetime.strptime(parameters['dateFrom'],datetimeFormat)
            dtTo = datetime.strptime(parameters['dateTo'],datetimeFormat)
            requestDuration = dtTo - dtFrom
            requestMins = requestDuration.total_seconds()
            propertyCount = len(properties)
            rowCount = int(sampleCount/propertyCount)
            sampleRate = round(((rowCount/math.floor(requestMins)) * 60),1)
            
            minTime = round(min(responseTimes),2)
            maxTime = round(max(responseTimes),2)
            sumTime = round(sum(responseTimes),2)
            avgTime = round((sumTime / requestCount),2)
            
            stats = {'min':minTime,
                     'max':maxTime,
                     'avg':avgTime,
                     'duration':str(requestDuration),
                     'rowCount':rowCount,
                     'sampleCount':sampleCount,
                     #'requestCount':requestCount,
                     #'url':requestUrl,
                     #'properties':properties,
                     'propertyCount':propertyCount,
                     'sampleRate':sampleRate}
            
            if self.showInfo:print("================")
            if self.showInfo:print ("{} tests".format(requestCount))
            if self.showInfo:print ("{} rows".format(rowCount))
            if self.showInfo:print ("{} samples".format(sampleCount))
            if self.showInfo:print ("{} sec min".format(minTime))
            if self.showInfo:print ("{} sec max".format(maxTime))
            #if self.showInfo:print ("{} sec sum".format(sumTime))
            if self.showInfo:print ("{} sec avg".format(avgTime))
            if self.showInfo:print ("{} properties - {}".format(propertyCount,','.join(properties)))
            if self.showInfo:print ("{} samples per min sample rate".format(sampleRate))
    
        return stats


    '''
    Method to retrieve raw data from an instrument, in the payload, in JSON format 
    from the rawdata service and captures and returns performance statistics
    which match filter criteria defined by a dictionary of parameters.
    
    The purpose of this function is to test performance of the rawdata service
    for comparison with a dataProductDelivery service for the download of identical data.
    
    see https://wiki.oceannetworks.ca/display/help/rawdata+service for usage and available parameters
    '''
    def _getRawPerformance_(self, 
                          parameters={}, #dictionary of web service filter parameters
                          requestCount=10): #Number of times to repeat the same request for averaging

        stats = {}
        url='{}api/rawdata'.format(self.baseUrl)
    
        parameters['method'] = "getByStation"
        parameters['token'] = self.token
        
        requestUrl = None
        responseTimes = []
        rowCount = None
        
        for i in range(requestCount):
            start = datetime.now()
            response = requests.get(url,params=parameters)
            end = datetime.now()
            delta = end - start
            execTime = delta.seconds + delta.microseconds/1E6
            
            if (response.ok):
                responseTimes.append(execTime)
                if self.showInfo:print("{}: {} sec".format(i+1,round(execTime,2)))
                if i==0:
                    requestUrl = response.url
                    payload = json.loads(util.toString(response.content))
            
                    if (payload):
                        data = payload['data']
                        if not data:
                            print('No records found')
                        if (payload['metadata']):
                            dataMetadata = payload['metadata']['dataMetadata']
                            if dataMetadata:
                                rowCount = dataMetadata['numberOfData']
            else:
                print('Error {} - {} : {}'.format(response.status_code,response.reason,response.url))
                break
                        
        
        if (len(responseTimes) > 0):
            datetimeFormat = '%Y-%m-%dT%H:%M:%S.%fZ' 
            dtFrom = datetime.strptime(parameters['dateFrom'],datetimeFormat)
            dtTo = datetime.strptime(parameters['dateTo'],datetimeFormat)
            requestDuration = dtTo - dtFrom
            requestMins = requestDuration.total_seconds()
            
            minTime = round(min(responseTimes),2)
            maxTime = round(max(responseTimes),2)
            sumTime = round(sum(responseTimes),2)
            avgTime = round((sumTime / requestCount),2)
            
            stats = {'min':minTime,
                     'max':maxTime,
                     'avg':avgTime,
                     'duration':str(requestDuration),
                     'rowCount':rowCount}
                     #'requestCount':requestCount,
                     #'url':requestUrl}
            
            if self.showInfo:print("================")
            if self.showInfo:print ("{} tests".format(requestCount))
            if self.showInfo:print ("{} rows".format(rowCount))
            if self.showInfo:print ("{} sec min".format(minTime))
            if self.showInfo:print ("{} sec max".format(maxTime))
            #if self.showInfo:print ("{} sec sum".format(sumTime))
            if self.showInfo:print ("{} sec avg".format(avgTime))
    
        return stats
     

    '''
    Method to download files from the archivefiles service and capture and return performance statistics
    which match filter criteria defined by a dictionary of parameters.
    
    The purpose of this function is to test performance of the archivefiles service
    for comparison with a dataProductDelivery service for the download of identical data.
    
    see https://wiki.oceannetworks.ca/display/help/archivefiles for usage and available parameters
    '''
    def _getFilesPerformance_(self, 
                            parameters={}, #dictionary of web service filter parameters
                            requestCount=10): #Number of times to repeat the same request for averaging
        
        stats = {}
        
        requestUrl = None
        responseTimes = []
        rowCount = None
        
        outPath = self.outPath
        
        pathPrefix = '_'.join([str(p).replace(':','') for p in parameters.values()])
       
        for i in range(requestCount):
            newOutPath = '{0}/{1}_{2}'.format(outPath,pathPrefix,i)
            if (os.path.isdir(newOutPath)):
                os.rmdir(newOutPath)
            
            os.mkdir(newOutPath)
            self.outPath=newOutPath

            start = datetime.now()
            files = self.getFiles(parameters)
            execTime = (datetime.now() - start).total_seconds()
            
            if (len(files) > 0):
                responseTimes.append(execTime)
            else:
                print('Error downloading files')
                break
                        
        
        if (len(responseTimes) > 0):
            datetimeFormat = '%Y-%m-%dT%H:%M:%S.%fZ' 
            dtFrom = datetime.strptime(parameters['dateFrom'],datetimeFormat)
            dtTo = datetime.strptime(parameters['dateTo'],datetimeFormat)
            requestDuration = dtTo - dtFrom
            requestMins = requestDuration.total_seconds()
            
            minTime = round(min(responseTimes),2)
            maxTime = round(max(responseTimes),2)
            sumTime = round(sum(responseTimes),2)
            avgTime = round((sumTime / requestCount),2)
            
            stats = {'min':minTime,
                     'max':maxTime,
                     'avg':avgTime,
                     'duration':str(requestDuration)}

            
            if self.showInfo:print("================")
            if self.showInfo:print ("{} tests".format(requestCount))
            if self.showInfo:print ("{} sec min".format(minTime))
            if self.showInfo:print ("{} sec max".format(maxTime))
            if self.showInfo:print ("{} sec avg".format(avgTime))

        self.outPath = outPath
        
        return stats

    
    '''
    Method to test the performance of running a data product on the task server without downloading the files.
    The method runs the same request a number of times to determine the performance of the request
    and assess the accuracy of the estimates from the dataProductDelivery request method or to
    compare the performance between equivalent requests in 1.0 and 2.0 services.
    '''
    def _getDataProductUrlsPerformance_(self, 
                                      parameters={}, 
                                      maxRetries=10, 
                                      requestCount=10):
        
        stats = {}
        responseTimes = []
        
        for i in range(requestCount):
            start = datetime.now()
            self.orderDataProduct(parameters, maxRetries, True)
            end = datetime.now()
            delta = end - start
            execTime = delta.seconds + delta.microseconds/1E6
            responseTimes.append(execTime)
                                   
        
        if (len(responseTimes) > 0):
            datetimeFormat = '%Y-%m-%dT%H:%M:%S.%fZ' 
            dtFrom = datetime.strptime(parameters['begin'],datetimeFormat)
            dtTo = datetime.strptime(parameters['end'],datetimeFormat)
            requestDuration = dtTo - dtFrom
              
            minTime = round(min(responseTimes),2)
            maxTime = round(max(responseTimes),2)
            sumTime = round(sum(responseTimes),2)
            avgTime = round((sumTime / requestCount),2)
            
            stats = {'min':minTime,
                     'max':maxTime,
                     'avg':avgTime,
                     'duration':str(requestDuration)}
            
            if self.showInfo:print("================")
            if self.showInfo:print ("{} tests".format(requestCount))
            if self.showInfo:print ("{} sec min".format(minTime))
            if self.showInfo:print ("{} sec max".format(maxTime))
            #if self.showInfo:print ("{} sec sum".format(sumTime))
            if self.showInfo:print ("{} sec avg".format(avgTime))
    
        return stats
    
    
    '''
    Method to test the performance of running a data product on the task server and downloading the files.
    The method runs the same request a number of times to determine the performance of the request
    and assess the accuracy of the estimates from the dataProductDelivery request method or to
    compare the performance between equivalent requests in 1.0 and 2.0 services.
    '''
    def _getWriteDataProductToFilesPerformance_(self, 
                                              parameters={}, 
                                              maxRetries=10, 
                                              requestCount=10):
        stats = {}
        responseTimes = []
        requestRequestTimes = []
        runRequestTimes = []
        queuingTimes = []
        runningTimes = []
        transferringTimes = []
        downloadingTimes = []
        
        outPath = self.outPath
        
        pathPrefix = '_'.join([str(p).replace(':','') for p in parameters.values()])
        
        for i in range(requestCount):
            
            newOutPath = '{0}/{1}_{2}'.format(outPath,pathPrefix,i)
            if (os.path.isdir(newOutPath)):
                os.rmdir(newOutPath)
            
            os.mkdir(newOutPath)
            self.outPath=newOutPath
            
            start = datetime.now()
            runResults = self.orderDataProduct(parameters, maxRetries, False)
            end = datetime.now()
            delta = end - start
            execTime = delta.seconds + delta.microseconds/1E6
            responseTimes.append(execTime)
            
            runStats = runResults['stats']
            
            requestRequestTimes.append(runStats['requestRequestTime'])
            runRequestTimes.append(runStats['runRequestTime'])
            queuingTimes.append(runStats['queuingTime'])
            runningTimes.append(runStats['runningTime'])
            transferringTimes.append(runStats['transferringTime'])
            downloadingTimes.append(runStats['downloadingTime'])
                                   
        
        if (len(responseTimes) > 0):
            datetimeFormat = '%Y-%m-%dT%H:%M:%S.%fZ' 
            dtFrom = datetime.strptime(parameters['begin'],datetimeFormat)
            dtTo = datetime.strptime(parameters['end'],datetimeFormat)
            requestDuration = dtTo - dtFrom
              
            minOverallTime = round(min(responseTimes),2)
            maxOverallTime = round(max(responseTimes),2)
            sumOverallTime = round(sum(responseTimes),2)
            avgOverallTime = round((sumOverallTime / requestCount),2)
            
            minRequestRequestTime = round(min(requestRequestTimes),2)
            maxRequestRequestTime = round(max(requestRequestTimes),2)
            sumRequestRequestTime = round(sum(requestRequestTimes),2)
            avgRequestRequestTime = round((sumRequestRequestTime / requestCount),2)
            
            minRunRequestTime = round(min(runRequestTimes),2)
            maxRunRequestTime = round(max(runRequestTimes),2)
            sumRunRequestTime = round(sum(runRequestTimes),2)
            avgRunRequestTime = round((sumRunRequestTime / requestCount),2)
            
            minQueuingTime = round(min(queuingTimes),2)
            maxQueuingTime = round(max(queuingTimes),2)
            sumQueuingTime = round(sum(queuingTimes),2)
            avgQueuingTime = round((sumQueuingTime / requestCount),2)
            
            minRunningTime = round(min(runningTimes),2)
            maxRunningTime = round(max(runningTimes),2)
            sumRunningTime = round(sum(runningTimes),2)
            avgRunningTime = round((sumRunningTime / requestCount),2)
            
            minTransferringTime = round(min(transferringTimes),2)
            maxTransferringTime = round(max(transferringTimes),2)
            sumTransferringTime = round(sum(transferringTimes),2)
            avgTransferringTime = round((sumTransferringTime / requestCount),2)
            
            minDownloadingTime = round(min(downloadingTimes),2)
            maxDownloadingTime = round(max(downloadingTimes),2)
            sumDownloadingTime = round(sum(downloadingTimes),2)
            avgDownloadingTime = round((sumDownloadingTime / requestCount),2)
            
            
            stats = {'overall':{'min':minOverallTime,'max':maxOverallTime,'avg':avgOverallTime},
                     'requestRequest':{'min':minRequestRequestTime,'max':maxRequestRequestTime,'avg':avgRequestRequestTime},
                     'runRequest':{'min':minRunRequestTime,'max':maxRunRequestTime,'avg':avgRunRequestTime},
                     'queuing':{'min':minQueuingTime,'max':maxQueuingTime,'avg':avgQueuingTime},
                     'running':{'min':minRunningTime,'max':maxRunningTime,'avg':avgRunningTime},
                     'transferring':{'min':minTransferringTime,'max':maxTransferringTime,'avg':avgTransferringTime},
                     'downloading':{'min':minDownloadingTime,'max':maxDownloadingTime,'avg':avgDownloadingTime},
                     'duration':str(requestDuration)}
            
            if self.showInfo:print("================")
            if self.showInfo:print ("{} tests".format(requestCount))
            if self.showInfo:print ("{} sec min".format(minTime))
            if self.showInfo:print ("{} sec max".format(maxTime))
            #if self.showInfo:print ("{} sec sum".format(sumTime))
            if self.showInfo:print ("{} sec avg".format(avgTime))
            
            
        
        self.outPath = outPath
    
        return stats        


    '''
    Method to return a dictionary of device metadata for a specific deviceId from the DeviceService
    see https://internal.oceannetworks.ca/pages/viewpage.action?title=DeviceService&spaceKey=DS
    '''    
    def _getDevice_(self, 
                  deviceId): #Device ID
        
        url='{}DeviceService'.format(self.baseUrl)
    
        parameters = {"operationtype":1, 
                      'effectivedate':'01-Jan-2000 00:00:00'}
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
        if (response.ok):
            try:
                result = json.loads(util.toString(response.content))
            except ValueError:
                print('Error calling: {}'.format(response.url))
                print("Message : {}".format(response.content))
                return None
            
            if (not isinstance(result,basestring)):
                devices = [d for d in result if d['deviceId'] == deviceId]
                if (len(devices)) >= 1:
                    return devices[0]
                else:
                    return None
            else: #Returns a message of the reason for failure
                print("Error: {}".format(result))
    
        if (self.showInfo): print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
 
    '''
    Method to return the name of a device using a specific deviceId from the DeviceService
    see https://internal.oceannetworks.ca/pages/viewpage.action?title=DeviceService&spaceKey=DS
    '''    
    def _getDeviceName_(self, 
                      deviceId): #Device ID
        
        url='{}DeviceService'.format(self.baseUrl)
    
        parameters = {'operationtype':1, 'effectivedate':'01-Jan-2000 00:00:00'}
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
        if (response.ok):
            try:
                result = json.loads(util.toString(response.content))
            except ValueError:
                print('Error calling: {}'.format(response.url))
                print("Message : {}".format(response.content))
                return None
                
            
            if (result):
                if (not isinstance(result,basestring)):
                    devices = [d['deviceName'] for d in result if d['deviceId'] == deviceId]
                    if (len(devices)) >= 1:
                        return devices[0]
                    else:
                        return None
                else: #Returns a message of the reason for failure
                    print("Error: {}".format(result))
            
    
        if (self.showInfo):print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
    
    
    '''
    Method to return a dictionary of Device Dates for a specific deviceId from the DeviceService
    see https://internal.oceannetworks.ca/pages/viewpage.action?title=DeviceService&spaceKey=DS
    '''
    def _getDeviceDates_(self, 
                       deviceId): #Device ID
        
        dict = {}
        sensorIds = []
        url='{}DeviceService'.format(self.baseUrl)
    
        parameters = {"operationtype":3}
        parameters['deviceids'] = deviceId
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
        if (response.ok):
            try:
                result = json.loads(util.toString(response.content))
            except ValueError:
                print('Error calling: {}'.format(response.url))
                print("Message : {}".format(response.content))
                return None
            
    
            if (result):
                payload = result['payload']
                if (payload):
                    for d in payload['devices']:
                        deviceId = d['device']['id']
                        dict[deviceId] = d['dates']
                        
                    
    
        if (self.showInfo):print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        
        return dict
    
    
    '''
    Method to return a list of sensorId values for a specific deviceId from the DeviceService
    see https://internal.oceannetworks.ca/pages/viewpage.action?title=DeviceService&spaceKey=DS
    '''
    def _getSensorIds_(self, 
                     deviceId): #Device ID

        sensorIds = []
        url='{}DeviceService'.format(self.baseUrl)
    
        parameters = {"operationtype":3}
        parameters['deviceids'] = deviceId
    
        start = datetime.now()
        response = requests.get(url,params=parameters)
        end = datetime.now()
        if (response.ok):
            content = json.loads(util.toString(response.content))
    
            if (content):
                payload = content['payload']
                if (payload):
                    devices = payload['devices']
                    for d in devices:
                        sensors = d['sensors']
                        sensor = sensors['sensor']
                        sensorIds = [s['id'] for s in sensor]
                        lst = [('{} - {}'.format(s['id'],s['name'])) for s in sensor]
    
                        print(lst)
    
        if (self.showInfo):print('URL: {}?{}'.format(url,('&'.join(['{}={}'.format(i[0],i[1]) for i in parameters.items()]))))
        
        return sensorIds
    
    def __remapKeys__(self,dict):
        keys = []
        for k in dict.keys():
            keys.append(k)
            
        for key in keys:
            if (key in self.filterMap.keys()):
                dict[self.filterMap[key]] = dict[key]
                del dict[key]
        
        return dict

if __name__ == '__main__':
    ''' '''
    util.printWithEnd('test')
    print ('  testing')

