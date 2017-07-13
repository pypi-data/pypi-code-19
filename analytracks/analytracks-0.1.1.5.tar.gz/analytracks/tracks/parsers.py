from datetime import datetime
import pandas as pd
import numpy as np


import lxml.etree as etree

import os
import numpy as np
import math

import simplejson
import urllib


def parse(path):
    if path.endswith('.tcx'):
        return tcxparse(path)   
        
    if path.endswith('.gpx') or path.endswith('.xml'):
        return gpxparse(path)


    if path.endswith('.txt'):
        return txtparse(path)


def tcxToCsv(athlete,activityId):
    '''
    tcx containing hr and power (from pedal torque) to csv

    '''
    infile='/DATA/tcx/'+athlete+'/'+activityId+'.tcx'
    outFolder='/DATA/csv/raw/'+athlete+'/'
    
    if not os.path.exists(outFolder):
        os.mkdir(outFolder)
    
    outFile=outFolder+activityId+'.csv'
    track=tcx(path)
    track.to_csv(outFile)

def gpxparse(infile):
    ns1 = 'http://www.topografix.com/GPX/1/1'
    ns2 = 'http://www.garmin.com/xmlschemas/TrackPointExtension/v1'
    root = etree.parse(infile).getroot()
    points=root.findall('*/*/{http://www.topografix.com/GPX/1/1}trkpt') 

    t0 = pd.to_datetime(points[0].find('{%s}time' %ns1).text)
    df = pd.DataFrame()
    
    for point in points:
        
        # time
        tx = pd.to_datetime(point.find('{%s}time' %ns1).text)
        dtx=tx-t0
        dtxs = dtx.total_seconds()
        
        #position
        try:
            lat=float(point.attrib['lat'])
            lon=float(point.attrib['lon'])
        except:
            lat=float('NaN')
            lon=float('NaN')
            
        # HR
        try:
            hr=float( point.find('{%s}extensions' %ns1)\
            .find('{%s}TrackPointExtension' %ns2)\
            .find('{%s}hr' %ns2).text )
        except:
            hr=float('NaN')    
        
        # Altitude
        try:
            ele=float(point.find('{%s}ele' %ns1).text)
        except:
            ele=float('NaN')
        
        # Distance (not implemeted for gpx yet)
        try:
            dist=float(point.find('{%s}DistanceMeters' %ns1).text)
        except:
            dist=float('NaN')

        # Cadence (not implemeted for gpx yet)
        try:
            cadance=float(point.find('{%s}Cadence' %ns1).text)
        except:
            cadance=float('NaN')
            
        # Speed (not implemeted for gpx yet)        
        try:
            speed=float(point.find('{%s}Extensions' %ns1) \
                        .find('{%s}TPX' %ns2).find('{%s}Speed' %ns2).text)
        except:
            speed=float('NaN') 
        
        # power (not implemeted for gpx yet)  
        try:
            power=float(point.find('{%s}Extensions' %ns1) \
                        .find('{%s}TPX' %ns2).find('{%s}Watts' %ns2).text)
        except:
            power=float('NaN')
        
        # Elevation
        data = {
            'timestamp':tx,
            'hr':hr, 
            'lat':lat,
            'lon':lon,
            'ele':ele,
            'time_s':dtxs
            }
        dfn = pd.DataFrame([data])
        df = df.append(dfn,ignore_index=True)

    otherData = {'Device':'?',
            'Author':'?',
            'Version':'?' }
            
    return df, otherData
        
def tcxparse(infile): 

    # should also return meta data

    ns1 = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
    ns2 = 'http://www.garmin.com/xmlschemas/ActivityExtension/v2'
    root = etree.parse(infile).getroot()
    points=root.findall('*/*/*/*/{%s}Trackpoint'%(ns1))


    t0 = pd.to_datetime(points[0].find('{%s}Time' %ns1).text)
    df = pd.DataFrame()

    for point in points:
        # Time
        
        tx = pd.to_datetime(point.find('{%s}Time' %ns1).text)
        dtx=tx-t0
        dtxs = dtx.total_seconds()
        
        # Position
        try:
            lat=float(point.find('{%s}Position' %ns1).find('{%s}LatitudeDegrees' %ns1).text)
            lon=float(point.find('{%s}Position' %ns1).find('{%s}LongitudeDegrees' %ns1).text)
        except:
            lat=float('NaN')
            lon=float('NaN')
            
        # HR
        try:
            hr=float( point.find('{%s}HeartRateBpm' %ns1).find('{%s}Value' %ns1).text )
        except:
            hr=float('NaN')    
        
        # Altitude
        try:
            ele=float(point.find('{%s}AltitudeMeters' %ns1).text)
        except:
            ele=float('NaN')
        
        # Distance
        try:
            dist=float(point.find('{%s}DistanceMeters' %ns1).text)
        except:
            dist=float('NaN')

        # Cadence 
        try:
            cadance=float(point.find('{%s}Cadence' %ns1).text)
        except:
            cadance=float('NaN')
            
        # Speed              
        try:
            speed=float(point.find('{%s}Extensions' %ns1) \
                        .find('{%s}TPX' %ns2).find('{%s}Speed' %ns2).text)
        except:
            speed=float('NaN') 
        
        try:
            power=float(point.find('{%s}Extensions' %ns1) \
                        .find('{%s}TPX' %ns2).find('{%s}Watts' %ns2).text)
        except:
            power=float('NaN')
        
        # Elevation
        data={
            'timestamp':tx,
            'hr':hr, 
            'lat':lat,
            'lon':lon,
            'po':power,
            'ele':ele,
            'dist':dist,
            'speed':speed,
            'time_s':dtxs
            }
        dfn = pd.DataFrame([data])
        df = df.append(dfn,ignore_index=True)

   
    otherData = getOtherData(root)
    return df, otherData
 
def getOtherData(xmlRoot):
    ns1 = 'http://www.garmin.com/xmlschemas/TrainingCenterDatabase/v2'
    device=xmlRoot.find('*/*/{%s}Creator/{%s}Name' %(ns1,ns1) ).text   
    try:
        author=xmlRoot.find('{%s}Author/{%s}Name' %(ns1,ns1)).text
        build=xmlRoot.findall('{%s}Author/{%s}Build/*/*' %(ns1,ns1))       
        version='.'.join([x.text for x in build])
    except:
        author='unknown'
        version='unknown'
    
     
    return {'Device':device,
            'Author':author,
            'Version':version }


