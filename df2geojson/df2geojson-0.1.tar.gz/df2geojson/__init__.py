# -*- coding: utf-8 -*-
"""
Created on Tue Aug 22 22:12:05 2017

@author: Tom
"""
import sys
import json

def convert(df, LonColName, LatColName, progress=True):
    #Define outside structure of geojson
    geojson = {"features":[], "type": "FeatureCollection"}
    #Get the columns of the dataframe 
    cols = df.columns.tolist()
    #Remove longitude and latitude from list
    cols.remove(LonColName)
    cols.remove(LatColName)
    #Iterate through dataframe
    for i in range(0, len(df.index)):
        tempDict = {"type": "Feature","properties": {},"geometry":{"coordinates": [],"type": "Point"}}
        #Add properties
        for prop in cols:
            try:
                tempDict["properties"][prop] = df.iloc[i][prop].tolist()
            except:
                tempDict["properties"][prop] = df.iloc[i][prop]
        #Add coordinates
        tempDict["geometry"]["coordinates"].append(df.iloc[i][LonColName].tolist())
        tempDict["geometry"]["coordinates"].append(df.iloc[i][LatColName].tolist())
        #Add to outside structure
        geojson["features"].append(tempDict)
        if progress == True:
            percent = str(round((i/len(df.index))*100,1))
            sys.stdout.write("\rProgress: %s percent complete" %percent)
            sys.stdout.flush()
    return geojson

def dump(path, geojson):
    with open(path, 'w') as fp:
        json.dump(geojson, fp)
        
def convert_and_dump(df, LonColName, LatColName, path, progress=True):
    #Define outside structure of geojson
    geojson = {"features":[], "type": "FeatureCollection"}
    #Get the columns of the dataframe 
    cols = df.columns.tolist()
    #Remove longitude and latitude from list
    cols.remove(LonColName)
    cols.remove(LatColName)
    #Iterate through dataframe
    for i in range(0, len(df.index)):
        tempDict = {"type": "Feature","properties": {},"geometry":{"coordinates": [],"type": "Point"}}
        #Add properties
        for prop in cols:
            try:
                tempDict["properties"][prop] = df.iloc[i][prop].tolist()
            except:
                tempDict["properties"][prop] = df.iloc[i][prop]
        #Add coordinates
        tempDict["geometry"]["coordinates"].append(df.iloc[i][LonColName].tolist())
        tempDict["geometry"]["coordinates"].append(df.iloc[i][LatColName].tolist())
        #Add to outside structure
        geojson["features"].append(tempDict)
        if progress == True:
            percent = str(round((i/len(df.index))*100,1))
            sys.stdout.write("\rProgress: %s percent complete" %percent)
            sys.stdout.flush()
    dump(path, geojson)
    