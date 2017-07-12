"""
solprim_tmyconvert.py
=====
Python package for TMY, EPW data conversion to TMY3 "previous" format

developed with Python3.5, tested with Python2.7

call module with 'import solprim_pckg.tmyconvert as conv'

functions included
    - convert_epw_to_csv (filename)
    - convert_tya_to_csv (filename)
    - convert_pvgis_to_csv (filename)


'solprimer' Python Solar Energy Calculation Primer
Copyright (C) 2017 by Gianguido Piani
contact information : <solarprimer@mailbox.org>

This program is free software: you can redistribute it and/or modify 
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful, 
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the 
GNU General Public License for more details.

For a full copy of the GNU General Public License see 
<http://www.gnu.org/licenses/>.


"""
# ===== ensure backward compatibility with Python2.7
from __future__ import division


import pandas as pd



def convert_tya_to_csv (filename=None):

    """
    convert TMY file in new TMY3 format into TMY3 previous format

    Function adapted from a similar function in PVLIB-PYTHON
    to read tmy data
    https://pvlib-python.readthedocs.io/en/latest/index.html
    https://pypi.python.org/pypi/pvlib/

    
    input:
    - filename with directory path, string

    output:
    - .csv file in TMY3 (previous format) including
        - metadata for the location
        - TMY data in a pandas dataframe

    - the location metadata is returned as value for the function

    the converted output file is saved in the same directory as the
    input file. It has the name of the original file with the addition
    '_CONVERT' and file type '.csv'

    =============================  

    the data in the original file is structured as follows
    orig_file row#1: values for Location ID,City,State,Time Zone,Latitude,
    Longitude,Elevation
    orig_file row#2: header for the following rows, different from old TMY3
    orig_file row#[3-8762]: values for above

    for the exact format description refer to the TMY3 Users Manual at
    http://www.nrel.gov/docs/fy08osti/43156.pdf

    =============================  

    output data structure
    
    =============================       =======================================
    TMYData field                       description
    =============================       =======================================
    Year                                Year of the TMY data
    Month                               1..12, January through December
    Day                                 1..28/30/31 Day of the Month
    Hour                                Hour 0..23
    ETR                                 Extraterrestrial radiation, W/m^2
    ETRN                                Extraterrestrial radiation normal,
                                        W/m^2
    GHI                                 Direct and diffuse (global) horizontal
                                        radiation received during 60 minutes
                                        prior to timestamp, Wh/m^2
    DNI                                 Amount of direct normal radiation
                                        (modeled) received during 60 mintues
                                        prior to timestamp, Wh/m^2
    DHI                                 Amount of diffuse horizontal radiation
                                        received during 60 minutes prior to
                                        timestamp, Wh/m^2
    Tdry                                Dry bulb temperature at the indicated
                                        time, deg C
    RH                                  Relative humidity at the indicated
                                        time, percent
    Pres                                Station pressure at the indicated time,
                                        mbar
    =============================       =======================================
    

    """

    # ===== read metadata
    #
    
    # open input file in read mode, read first row
    csv_file = open(filename, 'r')
    
    # read header data from row#1 in file
    # 'locData' is the metadata for selected location
    locData = csv_file.readline()    # read loc data into string

    # split the line into a list of strings, separate at commas
    locData = locData.split(',')

    locData.append('TMY3_new(TYA)')     # new value for 'Source'
    locData.append('USA')     # new value for 'Country'

    # build meta dictionary linking head indexes to values from locData 
    head = ['Location_ID', 'City', 'State', 'Time_Zone', 'Latitude',  
            'Longitude', 'Elevation', 'Source', 'Country']
    meta = dict(zip(head, locData))

    # for relevant fields: convert metadata strings to numeric values
    # float takes numeric values from a string, drops the rest
    meta['Latitude'] = round(float(meta['Latitude']),2)  
    meta['Longitude'] = round(float(meta['Longitude']),2)
    meta['Time_Zone'] = round(float(meta['Time_Zone']),2)
    meta['Elevation'] = int(float(meta['Elevation']))


    # show location metadata on terminal output
    print (meta)
    print ('')



    # ===== read TMY data
    #

    # the pandas 'read_csv' method can operate on already open file
    # header=1 to skip over the first row
    # row#2 contains the new headers, row# [3..8762] the tmy data
    # column names are read from row#2 and allocated automatically
    
    data = pd.read_csv(filename, header=1) 

    # close the file
    csv_file.close()


    # ===== process TMY data, prepare for output
    #

    # copy into new columns
    # the column names in the input new TMY file are different from
    # those in the previous TMY format
    # some columns are not relevant for solar energy applications,
    # they are commented away

    date    = data['Date (MM/DD/YYYY)']

    etr     = data['ETR (W/m^2)']
    etrn    = data['ETRN (W/m^2)']

    ghi     = data['GHI (W/m^2)']
    dni     = data['DNI (W/m^2)']
    dhi     = data['DHI (W/m^2)']
    tdry    = data['Dry-bulb (C)']
    #tdew    = data['Dew-point (C)']
    rh      = data['RHum (%)']
    pres    = data['Pressure (mbar)']
    #wspd    = data['Wspd (m/s)']
    #wdir    = data['Wdir (degrees)']
    #alb     = data['Alb (unitless)']

    # generate sequential values for year, month, day, hour

    year =  []
    month = []
    day =   []
    hour =  []

    month_len = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    h_idx = 0     # sequential hour counter (index)

    # iterate over months, days, hours, fill the respective columns
    for m in range(0, 12):
        for d in range(0, month_len[m]):
            for h in range(0, 24):
                year.append(date[h_idx][6:10])
                h_idx = h_idx+1
                month.append(m+1)
                day.append(d+1)
                hour.append(h)
       

    # build pandas dataframe 'data' from the lists and column names
    # 'Tdew','Wspd','Wdir','Albedo' not to be included in output file
    
    data = pd.DataFrame({ 'Year' : year,
                          'Month' : month,
                          'Day' : day,
                          'Hour' : hour,
                          'GHI' : ghi,
                          'DNI' : dni,
                          'DHI' : dhi,
                          'Tdry' : tdry,
                          #'Tdew' : tdew,
                          'RH' : rh,
                          'Pres' : pres,
                          #'Wspd' : wspd,
                          #'Wdir' : wdir,
                          #'Albedo' : alb,
                          'ETR' : etr,
                          'ETRN' : etrn })


    # ===== store new data in .csv file
    #

    # the converted file has the name of the original file
    # with addition '_CONVERT' and file type '.csv'
    filename1 = filename[0:-4] + '_CONVERT.csv' 

    # ===== store location metadata
    # open new csv file, write first two header rows with location data
    newfile = open(filename1, 'w')  # open newfile in write mode

    newfile.write('Source,Location_ID,City,State,Country,'
                  'Latitude,Longitude,Time_Zone,Elevation\n')

    newfile.write(meta['Source']+','+meta['Location_ID']+','+
                  meta['City']+','+ meta['State']+','+
                  meta['Country']+','+str(meta['Latitude'])+','+
                  str(meta['Longitude'])+','+
                  str(meta['Time_Zone'])+','+
                  str(meta['Elevation'])+'\n')
    
    newfile.close()


    # ===== store TMY data with pandas method 'to_csv()'
    
    # reopen output file in append mode
    # add data structured as .csv with pandas function
    # 'Tdew','Wspd','Wdir','Albedo' are not included in column list
                             
    with open(filename1, 'a') as newfile:
        data.to_csv(newfile, index=False,
                    columns=['Year','Month','Day','Hour','GHI',
                             'DNI','DHI','Tdry','RH',
                             'Pres','ETR','ETRN'])

    # close the file
    newfile.close()

    # print filename on shell display
    print ('file saved: ' + filename1)
    print ('')

    # exit and return the location metadata as dict
    
    return meta



def convert_epw_to_csv (filename=None):

    """
    convert TMY file in EPW format into TMY3 file previous format

    Part of the code is based on a similar function in PVLIB-PYTHON
    to read tmy data
    https://pvlib-python.readthedocs.io/en/latest/index.html
    https://pypi.python.org/pypi/pvlib/

    
    input:
    - filename with directory path, string

    output:
    - .csv file in TMY3 (previous format) including
        - metadata for the location
        - TMY data in a pandas dataframe

    - the location metadata is returned as value for the function

    the converted output file is saved in the same directory as the
    input file. It has the name of the original file with the addition
    '_CONVERT' and file type '.csv'

    =============================  

    the data in the original file, row#1 is structured as follows
    Field#1 -- 'LOCATION' (fixed text)
    Field#2 -- Location
    Field#3 -- State, region
    Field#4 -- Country code
    Field#5 -- Data source
    Field#6 -- Station ID
    Field#7 -- Latitude
    Field#8 -- Longitude (East = positive)
    Field#9 -- Time Zone
    Field#10 -- Elevation m

    =============================  

    orig_file row#2..8, headings for data on same rows
    DESIGN CONDITIONS
    TYPICAL/EXTREME PERIODS
    GROUND TEMPERATURES
    HOLIDAYS/DAYLIGHT SAVINGS
    COMMENTS 1
    COMMENTS 2
    DATA PERIODS


    orig_file  row#9..8768:
    Field#1 -- Year
    Field#2 -- Month
    Field#3 -- Day
    Field#4 -- Hour (range 1..24)
    Field#7 -- Tdry
    Field#8 -- Tdew
    Field#9 -- RH
    Field#10 -- Pressure in Pa
    Field#11 -- Extraterrestrial Horizontal Radiation (seldom reported)
    Field#12 -- Extraterr. Direct Normal Radiation (seldom reported)
    Field#14 -- GHI
    Field#15 -- DNI
    Field#16 -- DHI
    Field#21 -- Wind dir
    Field#22 -- Wind speed
    Field#33 -- Albedo

    values of '9's indicate missing data


    =============================  
    
    output data structure
    
    =============================       =======================================
    TMYData field                       description
    =============================       =======================================
    Year                                Year of the TMY data
    Month                               1..12, January through December
    Day                                 1..28/30/31 Day of the Month
    Hour                                Hour 0..23
    GHI                                 Direct and diffuse (global) horizontal
                                        radiation received during 60 minutes
                                        prior to timestamp, Wh/m^2
    DNI                                 Amount of direct normal radiation
                                        (modeled) received during 60 mintues
                                        prior to timestamp, Wh/m^2
    DHI                                 Amount of diffuse horizontal radiation
                                        received during 60 minutes prior to
                                        timestamp, Wh/m^2
    Tdry                                Dry bulb temperature at the indicated
                                        time (full hour), deg C
    Tdew                                Dew-point temperature at the
                                        indicated time (full hour), deg C
    RH                                  Relative humidity at the indicated
                                        time (full hour), percent
    Pres                                Station pressure at the indicated time
                                        (full hour), mbar
    Wspd                                Wind speed at the indicated time (full
                                        hour), meter/second
    Wdir                                Wind direction at the indicated time
                                        (full hour), degrees from north
                                        (360 = north; 0 = undefined, calm)
    Alb                                 Albedo, ratio of reflected solar
                                        irradiance to global horizontal
                                        irradiance, unitless
    =============================       =======================================
    
    """

    # ===== read metadata
    #
    
    # open epw file in read mode
    epw_file = open(filename, 'r')
    
    # read header data from row#1. 'locData' is data for selected location.
    locData = epw_file.readline()

    # split the full string into a list of substrings, divide at commas
    locData = locData.split(',')

    # build meta dictionary linking head indexes to values from locData
    # convert metadata strings to numeric values (only for relevant fields)
    meta = dict([('Source', str(locData[4])),
                 ('Location_ID', str(locData[5])),
                 ('City', str(locData[1])),
                 ('State', str(locData[2])),
                 ('Country', str(locData[3])),
                 ('Latitude', float(locData[6])),
                 ('Longitude', float(locData[7])),
                 ('Time_Zone', int(float(locData[8]))),
                 ('Elevation', int(float(locData[9])))])


    # show location metadata on terminal output
    print (meta)
    print ('')



    # ===== read TMY data, store in lists of length [0..8759]
    #
    
    '''
    in the following part the bulk of data from the .epw file is read
    and processed. The function 'pandas.read_csv' is not used here to
    avoid reading a large quantity of non-essential data.

    each parameter is extracted from each line independently, then added
    to the respective list. At the end of the procedure a pandas 
    dataframe is built from all the lists and is then saved as .csv file
    
    '''

    # define empty lists
    year    = []
    month   = []
    day     = []
    hour    = []
    ghi     = []
    dni     = []
    dhi     = []
    tdry    = []
    tdew    = []
    rh      = []
    pres    = []
    wspd    = []
    wdir    = []
    alb     = []


    # read data bulk from file
    # build new lists [0:8759] with same values as TMY3 files

    # the original EPW file 'epw_file' is still open
    # skip non-TMY data in header rows#2-8 (index i iterates 1..7 times)
    for i in range (0, 7):
        data = epw_file.readline() 

    # read TMY content
    for i in range (0, 8760):
        raw_data = epw_file.readline()

        # separate the comma-separated strings as different items
        # in a list
        data = raw_data.split(',')    

        # convert each string to numerical int/float value as necessary
        # add values to the lists
        # tdew, wspd, wdir, alb may be discarded. if needed, delete '#'s 
        year.append(int(data[0]))
        month.append(int(data[1]))
        day.append(int(data[2]))
        hour.append(int(data[3])-1)  # adapt hour count to TMY format
        ghi.append(int(data[13]))
        dni.append(int(data[14]))
        dhi.append(int(data[15]))
        tdry.append(float(data[6]))
        # tdew.append(float(data[7]))
        rh.append(int(data[8]))
        pres.append(int(data[9])/100)
        # wspd.append(float(data[21]))
        # wdir.append(int(data[20]))
        # alb.append(float(data[32]))


    # close the input file
    epw_file.close()

    
    # ===== store new data in .csv file
    #

    # the converted file receives the name of the original file
    # with addition '_CONVERT' and file type '.csv'
    filename1 = filename[0:-4] + '_CONVERT.csv' 

    # open new csv file
    # the output file is saved in the same directory as the input file

    # ===== store location metadata
    # write first two header rows with location data

    newfile = open(filename1, 'w')  # open newfile in write mode

    newfile.write('Source,Location_ID,City,State,Country,'
                  'Latitude,Longitude,Time_Zone,Elevation\n')

    newfile.write(meta['Source']+','+meta['Location_ID']+','+
                  meta['City']+','+ meta['State']+','+
                  meta['Country']+','+str(meta['Latitude'])+','+
                  str(meta['Longitude'])+','+
                  str(meta['Time_Zone'])+','+
                  str(meta['Elevation'])+'\n')
    
    newfile.close()


    # ===== prepare TMY data for storage
    #
    
    # build pandas dataframe 'data' from the lists and column names
    # the columns 'Tdew','Wspd','Wdir', and 'Albedo' are not added 
    # if needed, remove the comments '#'
    
    data = pd.DataFrame({ 'Year' : year,
                          'Month' : month,
                          'Day' : day,
                          'Hour' : hour,
                          'GHI' : ghi,
                          'DNI' : dni,
                          'DHI' : dhi,
                          'Tdry' : tdry,
                          #'Tdew' : tdew,
                          'RH' : rh,
                          'Pres' : pres,
                          #'Wspd' : wspd,
                          #'Wdir' : wdir,
                          #'Albedo' : alb
                            })


    # ===== store TMY data with pandas method 'to_csv()'
    #
    
    # reopen output file in append mode
    # add data structured as .csv with pandas function
    
    with open(filename1, 'a') as newfile:
        data.to_csv(newfile, index=False,
                    columns=['Year','Month','Day','Hour','GHI',
                             'DNI','DHI','Tdry','RH','Pres'])

    # close the file
    newfile.close()

    # print filename on shell display
    print ('file saved: ' + filename1)
    print ('')


    # exit and return the location metadata as dict
    
    return meta




def convert_pvgis_to_csv (filename=None):

    """
    convert TMY file in PVGIS format into TMY3 previous format

    Part of the code is based on a similar function in PVLIB-PYTHON
    to read tmy data
    https://pvlib-python.readthedocs.io/en/latest/index.html
    https://pypi.python.org/pypi/pvlib/

    

    read TMY file as generated by PVGIS (ver.5), produce .csv TMY3
    file (previous format) 
    
    input:
    - filename with directory path, string

    output:
    - .csv file in TMY3 (previous format) including
        - metadata for the location
        - TMY data in a pandas dataframe

    - the location metadata is returned as value for the function

    PVGIS TMY files metadata contains only location latitude, longitude,
    height, but no name, country, datasource
    
    as location name in the output file is taken the input filename up
    to 16 characters. For this reason it is recommended to rename PVGIS
    files with the desired location.
    
    the converted output file is saved in the same directory as the
    input file. It has the name of the original file with the addition
    '_CONVERT' and file type '.csv'

    PVGIS TMY files are generated at
    http://re.jrc.ec.europa.eu/pvgis.html

    Attention! THe PVGIS function returns data for the UTC time zone.
    For precise solar path calculations the time reference must be
    corrected for the applicable time zone.

    =============================  

    the data in the original file is structured as follows
    orig_file row#1: string "Latitude: 12.345678"
    orig_file row#2: string "Longitude: 12.345678"
    orig_file row#3: string "Elevation: 12.345678"
    orig_file row#4: string "Month, Chosen year"
    orig_file row#5-16: values for month [1-12] and the year from
    which TMY data was extracted

    orig_file row#17: field headers
    orig_file row#[18-8777]: field values

    Field#1 -- Date&Time (UTC)
    Field#2 -- Dry bulb temperature (deg. C)
    Field#3 -- Relative Humidity (%)
    Field#4 -- Global horizontal irradiance (W/m2) 
    Field#5 -- Direct (beam) normal Irradiance (W/m2)
    Field#6 -- Diffuse horizontal irradiance (W/m2)
    Field#7 -- Infrared radiation downwards (W/m2)
    Field#8 -- Windspeed (m/s)
    Field#8 --  Wind direction (deg.)
    Field#10 -- Air pressure (Pa)

    =============================  

    output data structure
    
    the columns 'Tdew', 'Alb' are not added to output as PVGIS file
    does not contain this information

    the columns 'Wspd', 'Wdir' are not added to output as the data
    is not required for solar performance calculations
  

    =============================       =======================================
    TMYData field                       description
    =============================       =======================================
    Year                                Year of the TMY data
    Month                               1..12, January through December
    Day                                 1..28/30/31 Day of the Month
    Hour                                Hour 0..23
    GHI                                 Direct and diffuse (global) horizontal
                                        radiation received during 60 minutes
                                        prior to timestamp, Wh/m^2
    DNI                                 Amount of direct normal radiation
                                        (modeled) received during 60 mintues
                                        prior to timestamp, Wh/m^2
    DHI                                 Amount of diffuse horizontal radiation
                                        received during 60 minutes prior to
                                        timestamp, Wh/m^2
    Tdry                                Dry bulb temperature at the indicated
                                        time, deg C
    RH                                  Relative humidity at the indicated
                                        time, percent
    Pres                                Station pressure at the indicated time,
                                        mbar
    =============================       =======================================
    

    """
    # ===== define metadata
    #
    
    # build city, country name
    # the city name is filename before extension, max 'n_len' chars
    # drop content until last "/" that indicates directory
    # put a '.csv' extension
    #

    n_len = 16
    s_pos = filename.rfind('/') # find last instance of "/" in string

    directory = filename[:s_pos+1]   # directory needed later

    # extract city name from filename
    city = filename[s_pos+1:-4][:n_len] # 'clean' filename less extension
    country = 'SUN'     # 'SUN' country code currently not assigned by ISO


    # ===== open file in read mode
    csv_file = open(filename, 'r')

    # read row#1, extract latitude value from string, convert to float
    r = csv_file.readline()[0:20]
    # scan the string to detect figures 0..9, dot '.', or minus '-'
    s = ''.join(x for x in r if (x.isdigit() or (x == '.') or (x == '-')))
    latitude = round (float(s), 2)

    # read row#2, extract longitude value from string, convert to float
    r = csv_file.readline()[0:20]
    s = ''.join(x for x in r if (x.isdigit() or (x == '.') or (x == '-')))
    longitude = round (float(s), 2)

    # read row#3, extract elevation value from string, convert to int
    r = csv_file.readline()[0:20]
    s = ''.join(x for x in r if (x.isdigit() or (x == '.') or (x == '-')))
    elevation = int(float(s))


    # ===== define other metadata, produce dictionary
    timezone = 0
    location_ID = '999000'
    state = 'AX'
    source = 'PVGIS'
    locData = (location_ID, city, state, timezone, latitude, longitude,
               elevation, source, country)

    # build meta dictionary linking head indexes to values from locData 
    head = ['Location_ID', 'City', 'State', 'Time_Zone', 'Latitude',  
            'Longitude', 'Elevation', 'Source', 'Country']
    meta = dict(zip(head, locData))


    # show location metadata on terminal output
    print (meta)
    print ('')


    # ===== read bulk data from input file, fill in lists/columns
    #
    # skip over initial rows with empty calls
    # row=17 contains the new headers, row=[18..8777] the data
    # column names will be read from row=17 and allocated automatically
    
    
    for i in range (0, 14):         # skip rows
        r = csv_file.readline()


    # define empty lists
    year =  []
    month = []
    day =   []
    hour =  []
    ghi =   []
    dni =   []
    dhi =   []
    tdry =  []
    rh  =   []
    pres =  []
    #wspd =  []
    #wdir =  []


    # data string example
    # '01/01/2008 00:00:00,1.9,79.63,0,0,0,240.2,1.83,168,99771'

    # strings may contain the character sequence '+AC0', unclear why
    # that needs to be cleaned up

    for i in range (0, 8760):
        r = csv_file.readline()
        
        # delete all instances of '+AC0'
        r_clean = r.replace('+AC0', '')   

        # should any other strange strings be found in the data
        # they should be removed here

        # split the line into a list of strings, separate at commas
        r_data = r_clean.split(',')

        year.append(int(r_data[0][6:10]))
        month.append(int(r_data[0][3:5]))
        day.append(int(r_data[0][0:2]))
        hour.append(int(r_data[0][11:13]))

        tdry.append(round(float(r_data[1]), 1))
        rh.append(int(round(float(r_data[2]),0)))

        ghi.append(int(float((r_data[3]))))
        dni.append(int(float((r_data[4]))))
        dhi.append(int(float((r_data[5]))))

        #wspd.append(round(float(r_data[7]), 1))  # unimportant parameter
        #wdir.append(int(r_data[8]))              # unimportant parameter
        pres.append(int(0.01*float(r_data[9])))   # pressure Pa to mbar


    # close the input file
    csv_file.close()


    # ===== store new data in .csv file via pandas dataframe structure

    # the converted file receives the name of the city from original
    # file with addition '_CONVERT' and file type '.csv'
    filename1 = directory + city + '_CONVERT.csv'

    # open new csv file
    # the output file is saved in the same directory as the input file

    # ===== store location metadata
    # write first two header rows with location data

    newfile = open(filename1, 'w')  # open newfile in write mode

    newfile.write('Source,Location_ID,City,State,Country,'
                  'Latitude,Longitude,Time_Zone,Elevation\n')

    newfile.write(meta['Source']+','+meta['Location_ID']+','+
                  meta['City']+','+ meta['State']+','+
                  meta['Country']+','+str(meta['Latitude'])+','+
                  str(meta['Longitude'])+','+
                  str(meta['Time_Zone'])+','+
                  str(meta['Elevation'])+'\n')
    
    newfile.close()


    # ===== prepare TMY data for storage
    #
    
    # build pandas dataframe 'data' from the lists and column names
    # the columns 'Wspd' and 'Wdir' are not added 
    # if needed, remove the '#' comments
    
    # build pandas dataframe 'data' from the lists and column names
    data = pd.DataFrame({ 'Year' : year,
                          'Month' : month,
                          'Day' : day,
                          'Hour' : hour,
                          'GHI' : ghi,
                          'DNI' : dni,
                          'DHI' : dhi,
                          'Tdry' : tdry,
                          'RH' : rh,
                          'Pres' : pres,
                          #'Wspd' : wspd,
                          #'Wdir' : wdir

                            })


    # ===== store TMY data with pandas method 'to_csv()'
    #
    
    # reopen output file in append mode
    # add data structured as .csv with pandas function
    
    with open(filename1, 'a') as newfile:
        data.to_csv(newfile, index=False,
                    columns=['Year','Month','Day','Hour','GHI',
                             'DNI','DHI','Tdry','RH','Pres' ])


    # close the file
    newfile.close()

    # print filename on shell display
    print ('file saved: ' + filename1)
    print ('')


    # exit and return the location metadata as dict
    
    return meta


