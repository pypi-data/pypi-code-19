"""
solprim_tmyutility.py
=====
Python function package for TMY data input, processing and presentation

developed with Python3.5, tested with Python2.7

call module with 'import solprim_pckg.tmyutility as tmy'

functions included
    - tmy_readcsv (filename)
    - tmy_daily_average (datalist)
    - tmy_daily_total (datalist)
    - tmy_monthly_total (datalist)
    - tmy_hdd_cdd (t_dry, hdd_threshold, hdd_ref, cdd_threshold, cdd_ref)
    - tmy_irradiation_stats (sol_irr)
    - tmy_low_ghi_days (ghi, ghi_threshold)
    - tmy_noontime_from_ghi (ghi_list)
    - tmy_yearplot (tmy_list, header_text, param_text)
    - tmy_yearplot_mult (tmy_tuple, label_tuple, header_text, param_text)
    - month_barchart (month_list, header_text, param_text, bar_color,
                      box_text)
    - tmy_heatmap (tmy_list, header_text)
    - tmy_plane_of_array (dni_list, dhi_list, latitude, longitude,
                          timezone, plane_azim, plane_tilt)


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


import numpy as np
import pandas as pd

import matplotlib.pyplot as plt



def tmy_readcsv (filename=None):

    """
    read a TMY file stored as .csv into a pandas dataframe

    Function adapted from a similar function in PVLIB-PYTHON
    https://pvlib-python.readthedocs.io/en/latest/index.html
    https://pypi.python.org/pypi/pvlib/

    
    the function works with files in TMY2, previous TMY3 format
    it does not work with INTL .csv files from the SAM dataset
    because the metadata header structure is different

    input:
    - filename with directory path, string

    output: tuple with
    - metadata for the location
    - TMY data in a pandas dataframe

    =============================  

    the data in the original file is structured as follows
    orig_file row#1: Source,Location ID,City,State,Country,Latitude,
    Longitude,Time Zone,Elevation
    orig_file row#2: values for above
    orig_file row#3: Year,Month,Day,Hour,GHI,DNI,DHI,Tdry,Tdew,RH,
    Pres,Wspd,Wdir,Albedo
    orig_file row#[4-8763]: values for above

    in the input file the metadata must follow the structure of row#1,2
    
    the data of row#3, #[4..8763] must have names as indicated,
    columns may be added or omitted

    =============================  

    Return Tuple of the form (metadata, data)
    metadata : dict. The site metadata from row2 of csv file.
    data : pandas DataFrame with columns as described in the
    table below

    Note - the pandas 'read_csv' method identifies the columns by
    their headers. If some column is not present in the original file,
    it is not read, and not returned either.

    'Tdew', 'Wspd', 'Wdir', 'Alb' are not present in all files
    'ETR', 'ETRN' are present only in files converted from TMY3 (new
    format)

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
    Tdew                                Dew-point temperature at the
                                        indicated time, deg C
    RH                                  Relative humidity at the indicated
                                        time, percent
    Pres                                Station pressure at the indicated time,
                                        mbar
    ETR                                 Extraterrestrial radiation, W/m^2
                                        (TMY3 files in updated format)
    ETRN                                Extraterrestrial radiation normal,
                                        W/m^2, (TMY3 files in updated format)
    Wspd                                Wind speed at the indicated time,
                                        meter/second
    Wdir                                Wind direction at the indicated time,
                                        degrees from north (360 = north;
                                        0 = undefined, calm)
    Alb                                 Albedo, ratio of reflected solar
                                        irradiance to global horizontal
                                        irradiance, unitless
    =============================       =======================================
    

    """

    # ===== read metadata
    #
    
    # open input file in read mode, read first two rows
    csv_file = open(filename, 'r')
    
    # read header data from 2nd row in file
    # 'locData' is the metadata for selected location
    locData = csv_file.readline()    # empty call to jump over row#1
    locData = csv_file.readline()    # read loc data into string

    # split the full string into a list of substrings, divide at commas
    locData = locData.split(',')

    # build a meta dictionary linking head indexes to values from locData 
    head = ['Source', 'Location ID', 'City', 'State', 'Country',
            'Latitude', 'Longitude', 'Time Zone', 'Elevation']
    meta = dict(zip(head, locData))

    # for relevant fields: convert metadata strings to numeric values
    # 'float' reads numeric values from a string, drops the rest
    meta['Latitude'] = round(float(meta['Latitude']),2)  
    meta['Longitude'] = round(float(meta['Longitude']),2)
    meta['Time Zone'] = round(float(meta['Time Zone']),2)
    meta['Elevation'] = int(float(meta['Elevation']))


    # ===== read TMY data
    #
    
    # the pandas 'read_csv' method can operate on already open file
    # input pointer is set at the beginning of the file, header=2 to
    # skip over the first two rows
    # row#3 contains the new headers, row# [4..8763] the tmy data
    # column names are read from row#3 and allocated automatically
    
    data = pd.read_csv(filename, header=2) 

    # close the file
    csv_file.close()


    return meta, data



def tmy_daily_average (datalist):

    """
    from a TMY list with 8760 hourly values calculate the day average

    attention when calculating solar values (ghi/dni/dhi), as the sum
    is averaged over the full 24 hours, night hours included

    input:
    - list with 8760 values, float

    returns:
    - list with 365 average values, float

    """

    day_average = []    # list for the day averages

    # iterate over all days of the year
    for d in range (0, 365):
        day_sum = 0        # daily sum 

        for h in range (0, 24):
            h_idx = d*24 + h        # pointer for day, hour in 'datalist'
            day_sum = day_sum + datalist[h_idx]

        day_average.append(day_sum/24)


    return day_average
            
            


def tmy_daily_total (datalist):

    """
    from a TMY list with 8760 hourly values of cumulative variables
    (e.g., solar irradiation) calculate the daily total

   input data:
    - list with 8760 values of cumulative values

    output:
    - list with 365 total values

    """

    day_total = []    # list for the day totals

    # iterate over all days of the year
    for d in range (0, 365):
        day_sum = 0        # daily sum 

        for h in range (0, 24):
            h_idx = d*24 + h        # pointer for day, hour in 'datalist'
            day_sum = day_sum + datalist[h_idx]

        day_total.append(day_sum)


    return day_total
            
            


def tmy_monthly_total (datalist):

    """
    from a TMY dataset calculate monthly totals and other statistics

    from a TMY dataset of cumulative values (ghi, dni, dhi, but
    also e.g. rainfall) calculate the monthly and the year totals and
    the monthly and yearly averages

    input data:
    - list with 8760 cumulative values from a TMY dataset (the exact
    type does not need to be specified, as aggregation operations are
    the same), float
    
    output: tuple with
    - list of totals per calendar month [0..11]
    - list of the daily averages per calendar month [0..11]
    - total for the year
    - daily average for the year

    """

    month_total = 0
    month_sum = []      # list for totals in each month
    month_avg = []      # list for averages in each month


    month_len = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # absolute pointers to the first hour of each month (day 1, hour 1)
    # value#13 = 8760 is to keep indexing consistent in the assignments
    # hour_from, hour_to
    
    month_idx = [0, 744, 1416, 2160, 2880, 3624,
                 4344, 5088, 5832, 6552, 7296, 8016, 8760]
   
    # iterate over the months
    for m in range(0, 12):

        month_total = 0       # reset total value for current month

        hour_from = month_idx[m]
        hour_to = month_idx[m+1] 
         
        for h in range (hour_from, hour_to):  # hour_to is skipped over
            month_total = month_total + datalist[h]  # add up month total       

        month_sum.append(month_total)   #write month total in list
        month_avg.append(round(month_total/month_len[m],3))

    year_sum = sum(month_sum)
        
    return month_sum, month_avg, year_sum, round(year_sum/365, 3)




def tmy_hdd_cdd (t_dry, hdd_threshold=13, hdd_ref=18,
                 cdd_threshold=26, cdd_ref=24):

    """
    from TMY temp calculate heating (hdd) and cooling degree-days (cdd)


    from a TMY list with 8760 hourly values for temperature calculate
    the heating degree-days (hdd) and the cooling degree-days (cdd)

    calculation principle: iterate over all days of the year, consider
    only those days with average temperature equal or below the temperature
    hdd_threshold (equal or above cdd_threshold for cooling DD).
    Add up in the heat_degree_days the absolute difference of the average
    temperature for the considered day and the reference temperature hdd_ref.
    The procedure is similar for cooling DD, with the absolute difference
    between the average day temperature and the cdd reference.
    Return the total.

    The formula considers that heating is necessary for those days with
    average temperature below the threshold (or above the other threshold
    in the case of cooling). Heating must be provided to bring the indoors
    temperature to hdd_ref, or cooling to bring the temperature down to
    cdd_ref.

    input data:
    - list with 8760 temperature values
    - threshold temperature for hdd addition yes/no (default value: 13C)
    - reference temperature for hdd calculation (default value: 18C)    
    - threshold temperature for cdd addition yes/no (default value: 26C)
    - reference temperature for cdd calculation (default value: 24C)    

    all values integer or float

    output:
    tuple with
    - heating degree days, integer
    - cooling degree days, integer

    """

    heat_ddays = 0
    cool_ddays = 0

    # verify input data consistency,
    # otherwise the computation does not make sense
    if ((hdd_threshold < hdd_ref) and (cdd_threshold > cdd_ref)):

        # iterate over all days of the year
        for d in range (0, 365):

            day_temp = 0         

            # loop to calculate the day average temp
            for h in range (0, 24):
                h_idx = d*24 + h
                day_temp = day_temp + t_dry[h_idx]
            day_temp_avg = day_temp/24
               
            if (day_temp_avg <= hdd_threshold):
                heat_ddays = heat_ddays + (hdd_ref - day_temp_avg)

            if (day_temp_avg >= cdd_threshold):
                cool_ddays = cool_ddays + (day_temp_avg - cdd_ref)
                
    return int(round(heat_ddays, 0)), int(round(cool_ddays, 0))


            
            
def tmy_irradiation_stats (sol_irr):

    """
    from a ghi/dni/dhi list return key aggregated parameters 

    from a list of solar irradiation values (ghi, dni, dhi)
    return key aggregated parameters 

    input data:
    - list with 8760 ghi/dni/dhi values from a TMY dataset (the exact
    type does not need to be specified, as aggregation operations are
    the same), integer or float
    
    output: tuple with
    - irrad max on hourly basis (Wh), integer
    - irrad max for the day (Wh), integer
    - day number for irrad max (day 1 is January, 1), integer
    - irrad year sum (kWh), integer
    - irrad day average (kWh), float

    """

    day_irr_max = 0       # max value of daily irradiation
    day_number = 0 

    # iterate over all days of the year
    for d in range(0, 365):
        day_irr = 0       # ghi total over the day

        for h in range (0, 24):
            hour_idx = d*24 + h   # pointer [0..8759] to input list
            day_irr = day_irr + sol_irr[hour_idx]  # add up day total       

        if (day_irr > day_irr_max):
            day_irr_max = day_irr     # new value for max irrad
            day_number = d       # day of year

    irrad_max = max(sol_irr)     # max hour value in Wh/m2
    irrad_sum = sum(sol_irr)     # year total in Wh/m2
    year_sum_kwh = int(irrad_sum/1000)     # year total in kWh/m2
    irrad_day_avg = round((year_sum_kwh/365),2)   # day average in kWh/m2 


    return (irrad_max, day_irr_max, day_number,
            year_sum_kwh, irrad_day_avg)



def tmy_low_ghi_days (ghi_list, ghi_threshold=2000):

    """
    consecutive and total number of days in the year with low ghi value

    return the number of consecutive days and the total number of days
    in the year with total ghi insolation below a given threshold

    this indication helps in sizing storage capacity in PV systems

    input data:
    - list with 8760 ghi values from a TMY dataset, integer/float
    - ghi threshold value, integer/float

    output: tuple with
    - number of consecutive days with ghi < threshold, integer
    - total number of days with ghi < threshold, integer

    """

    day_count = 0     # count of consecutive days with ghi < threshold
    day_count_max = 0   # max value of day_count
    day_count_total = 0

    # iterate over all days of the year
    for d in range(0, 365):
        day_ghi = 0       # ghi total over the day

        for h in range (0, 24):     # calculate ghi for one day
            h_idx = d*24 + h       # pointer [0..8759] to ghi list data
            day_ghi = day_ghi + ghi_list[h_idx]  # add up ghi day total
            
        if (day_ghi < ghi_threshold):
            day_count = day_count + 1   # one consecutive day with low ghi
            day_count_total = day_count_total + 1
        else:
            if (day_count > day_count_max):     # is this largest value?
                day_count_max = day_count
                
            day_count = 0       # reset day_count


    return day_count_max, day_count_total




def tmy_noontime_from_ghi (ghi_list):

    """
    calculate the weighed time for ghi maximum on a day
    

    from the TMY ghi parameter calculate the weighed time for the ghi
    maximum on each day. Return a list with the calculated noon time
    for each day of the year [0..364].
    
    From a plot of the estimated noon time over the year can be
    recognized the constant shift that depends on timezone and longitude
    as well as the variable deviation of the equation of time.

    input data:
    - list with 8760 ghi values from a TMY dataset, integer/float
    
    output: tuple with
    - list with 365 values for noon time in decimal format or 'None'
    when the value could not be calculated
    - average of the valid values in the list = estimated noon time
    expressed as local time

    NOTE: in the "previous" TMY format the hour is indexed [0..23]. For
    cumulative data, such as GHI, DNI, DHI, it refers to the following
    one-hour period, i.e., '0' is the pointer to the full hour starting
    at 0 and ending at 1, '1' points to the hour between 1 and 2, etc.

    In the newer EPW and updated TMY datasets hours are in range [1..24]
    and refer to the hour period terminating at the timestamp.

    This function operates on the TMY "previous" format. The hour
    timestamp for the weighed average are therefore corrected with
    a factor = +0.5 to refer to the time midpoint of accumulated values.
    
    """

    noon_year_avg = 0      # accumulated value for noon, to calculate avg
    noon_count = 0          # number of accumulated values, for average
    noon_average = []       # average noon time as list to fill

    # iterate over all days of the year
    for d in range(0, 365):
        d_idx = d*24            # pointer to the 1st hour of each day
        ghi_day = 0             # ghi total over the day
        noon_weighed = 0        # weighed average for noon timepoint

        for h in range (0, 12):
            h_idx = d_idx + h       # pointer [0..8759] to ghi list data
            ghi_hour = ghi_list[h_idx]   # ghi value for the hour
            ghi_day = ghi_day + ghi_hour
            noon_weighed = noon_weighed + ghi_hour*(h+0.5)

        ghi_noon = ghi_day      # accumulated ghi values in first 1/2 day    
            
        for h in range (12, 24):
            h_idx = d_idx + h       # pointer [0..8759] to ghi list data
            ghi_hour = ghi_list[h_idx]
            ghi_day = ghi_day + ghi_hour
            noon_weighed = noon_weighed + ghi_hour*(h+0.5)

        # consider only those days for which the ghi total of each half
        # day is at least 30% of day total (otherwise the imbalance is
        # too high)
        if (ghi_day > 0):
            ghi_dev = ghi_noon/ghi_day
            
        if (ghi_day == 0) or (ghi_dev<0.3) or (ghi_dev>0.7):
                noon_average.append(None)
        else:
            noon_calc = round(noon_weighed/ghi_day, 2)  # calculated noon
            noon_average.append(noon_calc)
            noon_year_avg = noon_year_avg + noon_calc
            noon_count = noon_count + 1
            
    return noon_average, round(noon_year_avg/noon_count, 2)




def tmy_yearplot (tmy_list, header_text = '', param_text = ''):

    """
    plot the TMY value passed as list for the whole year

    input:
    - list with 8760 hourly or 365 daily data records
    - text for plot header string
    - parameter name string, for display

    output:
    - graphic plot with the TMY selected parameter over the year
    
    """

    # figure and subplot call 
    plt.figure()
    ax = plt.subplot(111)
  
    plt.grid(True)
    plt.xlabel('day of year', family='sans-serif', size=10)
    plt.ylabel(param_text, family='sans-serif', size=10)
    plt.title(header_text, family='sans-serif', size=10)

    # set limits for x_axis
    # length of x axis is the number of points of input string 8760/ 365
    xlength = len(tmy_list)

    if (xlength == 8760):
        xticks_ref = [0, 2190, 4380, 6570, 8760]
    else:
        xticks_ref = [0, 91, 183, 274, 365]
    
    plt.xlim(0, xlength)    
    plt.xticks(xticks_ref, ['Jan 1','Apr 1','Jul 1','Oct 1','Dec 31'])


    # plot the data
    plt.plot(tmy_list, color='b')
    

    # set limits for y_axis
    # get y coordinates after automatic scaling. If the minimum value
    # to be plotted is =0, then set Y-axis starting point =0

    ylim = plt.gca().get_ylim()     # get y coordinates after scaling
    ypos_min = ylim[0]
    ypos_max = ylim[1]

    # if min value to be plotted is =0, then set y min in graph = 0
    # the 'try' statement is used to avoid inconsistencies in the
    # determination of min value in list, when some value is 'None' 
    try:     
        if (min(tmy_list) == 0):
            ypos_min = 0
    except:
        pass
        
    plt.ylim(ypos_min, ypos_max)    

    # draw ticks
    plt.xticks(family='sans-serif',size=10)
    plt.yticks(family='sans-serif',size=10)

    plt.show()
    plt.close()

    return




def tmy_yearplot_mult (tmy_tuple, label_tuple, 
                       header_text = '', param_text = '',
                       ypos_ref = None):

    """
    plot the TMY values passed as list for the whole year

    input:
    - tuple with 2 or more lists with 8760 hourly or 365 daily data
    records, integer/ float
    - tuple with labels related to the lists
    - header_text, text for drawing header, string
    - param_text, y axis text (parameter name), string
    - ypos_ref: if explicitly passed, y axis starting value 

    output:
    - graphic plot with the TMY selected parameters over the year
    
    """

    # figure and subplot call 
    plt.figure()
    ax = plt.subplot(111)
  
    plt.grid(True)

    # set limits for x_axis
    # length of x axis is the number of points of input string 8760/ 365
    xlength = len(tmy_tuple[0])

    if (xlength == 8760):
        xticks_ref = [0, 2190, 4380, 6570, 8760]
    else:
        xticks_ref = [0, 91, 183, 274, 365]
    
    plt.xlim(0, xlength)    
    plt.xticks(xticks_ref, ['Jan 1','Apr 1','Jul 1','Oct 1','Dec 31'])


    # plot the data
    for i in range(0, len(tmy_tuple)):
        plt.plot(tmy_tuple[i], label=label_tuple[i])


    # set limits for y_axis
    # get y coordinates after automatic scaling. If the minimum value
    # to be plotted is =0, then set Y-axis starting point =0

    ylim = plt.gca().get_ylim()     # get y coordinates after scaling
    ypos_min = ylim[0]
    ypos_max = ylim[1]

    if (min(tmy_tuple[0]) == 0):
        ypos_min = 0

    if (ypos_ref != None):
        ypos_min = ypos_ref
        
    plt.ylim(ypos_min, ypos_max)

    plt.xlabel('day of year', family='sans-serif', size=10)
    plt.ylabel(param_text, family='sans-serif', size=10)
    plt.title(header_text, family='sans-serif', size=10)
    plt.legend()

    # draw ticks
    plt.xticks(family='sans-serif',size=10)
    plt.yticks(family='sans-serif',size=10)


    plt.show()
    plt.close()

    return




def month_barchart (month_list, header_text = '', param_text = '',
                    bar_color = 'm', box_text = ''):

    """
    plot a barchart for the values passed as list for the months 1-12
    
    input:
    - list with 12 monthly data values
    - text for barchart header string
    - text for parameter name, for y-axis display
    - bar_color, color for the barchart, string, default = 'm'

    basic colors - b: blue, g: green, r: red, c: cyan, m: magenta,
    y: yellow, k: black, w: white, '0.70': gray shade (proportional)


    output:
    - barchart plot with the monthly parameters over the year
    
    """
    
    # figure and subplot call 
    plt.figure()
    ax = plt.subplot(111)

    # plot barchart background data
    plt.grid(True, axis='y')

    plt.xlabel('month', family='sans-serif', size=10)
    plt.ylabel(param_text, family='sans-serif', size=10)

    plt.title(header_text, family='sans-serif', size=10)

    xticks_count = [1,2,3,4,5,6,7,8,9,10,11,12]
    xticks_label = ('Jan','Feb','Mar','Apr','May','Jun','Jul','Aug',
                    'Sep','Oct','Nov','Dec')
    plt.xticks(xticks_count, xticks_label)

    # if 'box_text' is passed place it in box at upper left corner

    if (len(box_text) > 0):
       xpos = 0.5
       ypos = max(month_list) * 0.88
       ax.text(xpos, ypos, box_text, family='sans-serif', size=10,
               color='k',
               bbox={'facecolor':'white', 'edgecolor':bar_color,
                     'alpha':0.5, 'pad':5})


    # plot graph
    plt.bar(xticks_count, height=month_list, color=bar_color)


    # show the figure
    plt.show()
    plt.close()

    return



def tmy_heatmap (tmy_list, header_text = ''):

    """
    plot input data as list with hourly values [0..8759] as heatmap
    
    day of year on x-axis, time of day on y-axis
    parameter value as color range

    input:
    - list with 8760 hourly data values
    - text for plot header string

    output:
    - heatmap plot with the parameter for each combination of
    day of year and time of day with color depending on parameter range,
    colorbar

    """

    # build a numpy array, initial values all=0
    t_array = np.zeros((24,365))    

    # copy input data into array, ordered per day and hour of the day
    for d in range (0, 365):
        for h in range (0, 24):
            hour_idx = d*24 + h    # pointer to the hour in the year
            t_array[h,d] = round(tmy_list[hour_idx], 1)

    # colormaps are shown in
    # http://scipy.github.io/old-wiki/pages/Cookbook/Matplotlib/Show_colormaps
    # from here is selected the color range in 'cmap=' in the plt.imshow call



    # figure and subplot call 
    plt.figure()
    ax = plt.subplot(111)
  
    
    # set the min-max color range automatically
    plt.imshow(t_array, cmap='jet', extent=[0,365,0,24], aspect=12,
               origin='lower')
    
    # the min-max color range can be set manually with the
    # variables vmin, vmax
    # plt.imshow(t_array, cmap='jet', extent=[0,365,0,24], aspect=12,
    #           origin='lower', vmin=0, vmax=1300)
    

    plt.colorbar(shrink=0.85)

    plt.grid(True)
    plt.title(header_text, family='sans-serif', size=10)

    plt.xlabel('day of year')
    plt.ylabel('hour of day')

    plt.xticks([0, 91, 182, 273, 365],
           ['Jan 1', 'Apr 1', 'July 1', 'Oct 1', 'Dec 31'], size=10)
    plt.yticks([0, 6, 12, 18, 24], ['0','6','12','18','24'], size=10)


    # display result
    plt.show()
    plt.close()

    return



def tmy_plane_of_array (dni_list, dhi_list, latitude=0, longitude=0, 
                        timezone=0, plane_azim=180, plane_tilt=0):

    """
    from TMY data calculate the yearly plane-of-array energy yield 

    the function accepts one tmy list for dni (beam) and one tmy list
    for dhi insolation values, the azimuth, tilt values for an oriented
    surface for solar energy collection and a location latitude. It
    returns the PlaneOfArray (POA) irradiation value on an hourly
    basis for the whole TMY year.

    results with reference to the unit surface (1 m2)
    
    input:
    - dni_list, list with 8760 DNI values from TMY dataset, integer/float
    - dhi_list, list with 8760 DHI values from TMY dataset, integer/float
    - latitude, latitude of the location (positive North of equator),
    float, default =0
    - longitude, longitude of the location (positive North of equator),
    float, default =0
    - timezone, positive East of Greenwich, integer/float 
    - plane_azim, azimuth of the oriented plane, in degrees
    (South is 180), float, default = 180
    - plane_tilt, tilt of the oriented plane in degrees
    (horizontal tilt is 0), float, default =0

    output:
    - poa_list, POA 8760 hourly values, float
    - dir_list, direct radiation on plane, 8760 hourly values, float 
    - dif_list, diffuse radiation on plane, 8760 hourly values, float
    - incid_list, beam angle of incidence on plane, 8760 hourly values,
    float

    """

    import math

    import solprim.solartimeposition as stp


    # convert input angles to radians
    latitude_rad = math.radians(latitude)
    plane_azim_rad = math.radians(plane_azim)
    plane_tilt_sin = math.sin(math.radians(plane_tilt))
    plane_tilt_cos = math.cos(math.radians(plane_tilt))

    # share of visible sky share for diffuse radiation, depends on tilt
    dhi_coeff = 0.5 * (1 + plane_tilt_cos)

    # year required for datetime input, 2015 as default (no leap year)
    year = 2015

    # list for the calculated Plane Of Array values
    poa_list = []
    dir_list = []
    dif_list = []
    incid_list = []


    # for the calculation of the angle over the inclined plane it is 
    # necessary to pass month, day, hour. These are generated here 
    # to avoid import of date, time columns from the TMY dataset.

    # month length, in days
    month_len = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

    # absolute pointers to the first hour (day 1, hour 1) of each month
    # in the TMY list
    month_ptr = [0, 744, 1416, 2160, 2880, 3624,
                 4344, 5088, 5832, 6552, 7296, 8016]

    day_of_year = 0
   
    # iterate over months, days, hours
    for m in range(0, 12):
        m_ptr = month_ptr[m]
        
        for d in range (0, month_len[m]):
            # d_ptr points to the first hour of day=d+1 and month=m+1
            d_ptr = m_ptr + d*24

            # day value for the solar declination, equation of time
            day_of_year = day_of_year + 1
            sol_decl = stp.solar_declination(day_of_year)
            sol_decl_rad = math.radians(sol_decl)

            eot = stp.equation_of_time (day_of_year)
            
            for h in range (0, 24):
                h_ptr = d_ptr + h   # pointer to year hour [0..8759]

                hour_poa = 0        # reset hourly values
                plane_dir = 0
                plane_dif = 0
                incid_angle = 0
                
                # calculate only for DNI>0 or DHI>0, sun above horizon
                dni = dni_list[h_ptr]
                dhi = dhi_list[h_ptr]

                if (dni > 0) or (dhi > 0):

                    # find solar position. The reference hour for
                    # calculations is 30 min earlier than the end of the
                    # full hour to which integral TMY data is referred

                    # calculate hour angle from solar time, add 0.5 hrs
                    # correction for eot, longitude, timezone is done
                    # in 'hour_angle_decimal' function

                    hra = stp.hour_angle_decimal(h + 0.5, eot,
                                                 longitude, timezone)
                    hra_rad = math.radians(hra)

                    # the function solar_azim_elev returns a tuple
                    sol_pos = stp.solar_azim_elev(sol_decl_rad,
                                                  hra_rad, latitude_rad)
                    sol_elev_sin = sol_pos[4]      # solar_elevation sin 
                    sol_elev_cos = sol_pos[5]      # solar_elevation cos 
                    sol_azim_rad = sol_pos[3]      # solar azimuth in rad

                    # incidence angle of solar radiation
                    # over the oriented plane
                    cos_theta = stp.incidence_factor(sol_elev_sin,
                                                     sol_elev_cos,
                                                     plane_tilt_sin,
                                                     plane_tilt_cos,
                                                     sol_azim_rad,
                                                     plane_azim_rad)

                    incid_angle = math.degrees(math.acos(cos_theta))

                    # direct radiation
                    plane_dir = dni*cos_theta

                    # diffuse radiation
                    plane_dif = dhi*dhi_coeff

                    # Plane Of Array irradiation for current hour
                    hour_poa = plane_dir + plane_dif


                # end of POA calculation for current hour
                # add values to lists
                poa_list.append(hour_poa)
                dir_list.append(plane_dir)
                dif_list.append(plane_dif)
                incid_list.append(round(incid_angle,2))


    return (poa_list, dir_list, dif_list, incid_list)

