import numpy as np
import simplejson
import urllib
import srtm
import os

import pkg_resources
google_ele_api_key_file = pkg_resources.resource_filename('analytracks.tracks', 'data/googleElevationApi.key')
try:
    with open(google_ele_api_key_file,'r') as f:
        google_ele_api_key = f.read()
except:
    google_ele_api_key = input('Please provide a google elevation api key if you have one:\n')
    with open(google_ele_api_key_file,'w') as f:
        f.write(google_ele_api_key)
        
        
def add_srtm_elevation(df):
    elevation_data = srtm.get_data() 
    validPositions= ~( np.isnan(df.lat) | np.isnan(df.lon) )   
    for i,point in df.ix[validPositions,].iterrows():
        df.ix[i,'srtmElevation'] = float(elevation_data.get_elevation(point.lat, point.lon))

    return df

def add_google_elevation(df,use_the_key=True,new_google_key=''):
    ''' for each valid location of the track, use google elvation api to 
    fetch its altitude
    '''
    global google_ele_api_key
    if new_google_key:
        with open(google_ele_api_key_file,'w') as f:
            f.write(new_google_key)  
        google_ele_api_key = new_google_key
    
    validPositions= ~( np.isnan(df.lat) | np.isnan(df.lon) ) 
    coordinates=np.array(df.ix[validPositions,['lat','lon']])
    coordinatesSplit=np.split(coordinates,range(100,len(coordinates),100))
    
    elevationArray = []
    for coordinatesI in coordinatesSplit:
        #print(coordinatesI)
        url=getRequestURL(coordinatesI,use_the_key)   

        response=[]
        attempt_max=5
        for x in range(0,attempt_max):
            try:
                response = simplejson.load(urllib.request.urlopen(url))
                break
            except:
                pass
        
        if not response:
            raise Exception('check your connection')
        
        if response['results']:
            for resultset in response['results']:
                elevationArray.append(resultset['elevation'])

        else:
            raise Exception(response['error_message']) 
                
        #except:
        #    raise Exception('something went wrong, check your internet connection or you google elevation api key. You may call the same function passing a valid api key')
            
                    
            
    df.ix[validPositions,'googleElevation']=elevationArray
            
    return df  
        
    
    
   



def getRequestURL(coordinates,use_the_key=True):
    # it also work without the key for 2500 querries  
    #ELEVATION_BASE_URL = 'https://maps.googleapis.com/maps/api/elevation/json?path='
    ELEVATION_BASE_URL = 'https://maps.googleapis.com/maps/api/elevation/json?locations='
        
    url=ELEVATION_BASE_URL
    for lat,lon in coordinates:
        url+="%f,%f|" %(lat,lon)
        
    #url+="&samples={}".format(len(coordinates))
    
    if use_the_key:
        url=url[0:-1]+"&key="+google_ele_api_key
    return url
    
    
def addElevationsToRsCsv(athlete,activityId):
    
    inFolder='/DATA/csv/rs_01/'+athlete+'/'
    inFile=inFolder+activityId+'.csv'
    
    outFolder='/DATA/csv/ele/'
    if not os.path.exists(outFolder):
        os.mkdir(outFolder)
        
    if not os.path.exists(outFolder+athlete):
        os.mkdir(outFolder+athlete)
    
    outFile=outFolder+athlete+'/'+activityId+'.csv'
    
    df=pd.read_csv(inFile,index_col=0)
    #df=addElevationSrtm(df)
    df=addElevationGoogle(df)
    
    df.to_csv(outFile)
