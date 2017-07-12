"""
power_load_profile.py
=====
generate a power load profile depending on time, tmy data, activity

developed with Python3.5, tested with Python2.7

process steps
- generate a load profile for different types of power loads
- save the load and its components as csv file

- some loads are dependent on ambient variables ghi, Tdry. These loads
are simulated only if a tmy file reference with ghi, Tdry is passed

generate a TMY-type load profile as function of time (day, hour) and
ambient parameters (ghi for illumination, tdry for heating/cooling)

    
input data:
- TMY dataset (directory, name) for GHI, Tdry values [0..8759]
- calendar parameters
- baseload
- time-related loads
- illumination loads
- heating loads
- cooling loads

output:
all values are integer
csv-format file for the hours of the year with rows numbered [0..8759]
and columns for
- month [1..12], integer
- day of month [1..31], integer
- hour of day [0..23], integer
- day of week [0..6], integer
- flag holiday=True
- time-related load (kWh), float (two decimal positions)
- illumination load (kWh), float (two decimal positions)
- heating load (kWh), float (two decimal positions)
- cooling load (kWh), float (two decimal positions)
- total load (kWh), float (two decimal positions)

Attention! when reading the .csv file into the spreadsheet program set
only the comma ',' as separator. The semicolon ';' is not a field separator,
but an input to the function processor.



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



# ===== Parameter manual input =====
#
# ===== TMY input file

#tmy_filename = 'TMY-EPW_ITA_Bologna161400_CONVERT.csv'     # Bologna
#tmy_filename = 'TMY-EPW_DEU_Berlin103840_CONVERT.csv'     # Berlin
#tmy_filename = 'TMY_USA_AZ_Phoenix722780_(TYA)_CONVERT.csv'     # Phoenix
#tmy_filename = 'TMY_USA_HI_HonoluluIntlAP911820_(TYA)_CONVERT.csv'     # Honolulu
tmy_filename = 'TMY_USA_NY-NewYork_JFK744860_(TYA)_CONVERT.csv'     # New York
#tmy_filename = 'TMY-EPW_SGP_Singapore486980_CONVERT.csv'

# ===== input directory
tmy_directory = 'data-TMY/'


# ===== output file and directory
out_directory = 'data-output/'
out_filename = 'load_profile_001.csv'


# ===== Calendar parameters
#
# - holiday: list of days of year to be considered as holiday and
# treated as weekend. Default values are Jan 1st (new year),
# Jan 26th (India), May 8th (Europe), Jun 12th (Russia), Jul 4th (USA),
# Sep 7th (Brazil), Oct 1st (China), Dec 25 (Christmas)
# - weekend: list with the days of the week [1..7], Monday=1, Sunday=7
# to be treated as non-work day
# - year_begin: day of the week [1..7] for Jan 1st

holiday = [1, 26, 128, 163, 185, 250, 274, 359]
weekend = [6, 7]
year_begin = 1

# ===== Baseload
# - baseload, integer
# typical baseload loads are computer servers, refrigeration for
# food storage, alarm devices, emergency lighting etc.
# the baseload depends little on external factors such as ambient
# temperature, time of day etc.

baseload=27400


# ===== Time-related loads
# - timeload_prof_wd - timeload profile for workdays, the share of
# timeload_peak to be considered for each hour (profile typical for
# industrial machinery with predefinite operation timepoints),
# values [0..23] in range [0..1]
# - timeload_prof_hd - timeload profile for holidays
# - timeload_peak - peak load for timeload

timeload_peak=10800

load_profile_wd = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.2, 0.4,
                   1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0,
                   1.0, 1.0, 1.0, 1.0, 1.0, 0.2, 0.1, 0.1]
load_profile_hd = [0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1,
                   0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1,
                   0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1, 0.1]

# ===== Illumination loads
# - illum_peak - load for illumination
# - illum_ghi - ghi threshold below which the illumination load
# is activated at nominal power
# - illum_hour_wd - indicates whether illumination can be activated
# as function of ghi at corresponding hour on weekdays 
# - illum_hour_hd - indicates whether illumination can be activated
# as function of ghi at corresponding hour on holidays

illum_peak=29500
illum_ghi=600

illum_hour_wd = [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0]
illum_hour_hd = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

# ===== Heating loads
# - heating_tmax - maximum temperature for heating load operation
# - heating_tmin - minimum temperature for heating load operation,
# at peak heating power
# - heating_peak - max heating power for t = heating_tmin
# the heating load for heating_tmin < t < heating_tmax is determined
# by linear interpolation

heat_tmin=-20
heat_tmax=12 
heat_peak=22000

# ===== Cooling loads
# - cooling_tmax - maximum temperature for cooling load operation,
# at peak cooling power
# - cooling_peak - max cooling power for t = cooling_tmax
# the cooling load for cooling_tmin < t < cooling_tmax is determined
# by linear interpolation

cool_tmin=25
cool_tmax=33
cool_peak=50000

# ===== end of manual input data



# =================================
# ========== main script ==========
# =================================
#

import datetime as dt
import pandas as pd

import solprim.tmyutility as tmy


# ===== read TMY data
try:
    tmy_data = tmy.tmy_readcsv(tmy_directory + tmy_filename)
    use_ambient_data = True
except:
    use_ambient_data = False


# show location data on terminal output

if use_ambient_data:
    print (tmy_data[0])
    country = tmy_data[0]['Country']
    city = tmy_data[0]['City']
else:
    print ('no input datafile')
    country = 'undefined'
    city = ''
    
print ('')


# ===== list, parameter initialization

month = []
day = []
hour = []
weekday = []
workday = []

day_of_week = year_begin
day_of_year = 1

# length of month in days
month_len = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

for m in range (0, 12):
    for d in range (0, month_len[m]):

        if ((day_of_week in weekend) or (day_of_year in holiday)):
            workday_day = False
        else:
            workday_day = True

        for h in range (0, 24):
            month.append(m+1)
            day.append(d+1)
            hour.append(h)
            weekday.append(day_of_week)
            workday.append(workday_day)

        # update the day_of_year, day_of_week counters
        day_of_year = day_of_year + 1

        if (day_of_week < 7):
            day_of_week = day_of_week + 1
        else:
            day_of_week = 1


# ===== calculation of time-related load

base_load = []
work_load = []

for d in range (0, 365):

    workday_day = workday[d*24]     # points to the first hour of the day

    for h in range (0, 24):

        if workday_day:
            workload_coeff = load_profile_wd[h]
        else:
            workload_coeff = load_profile_hd[h]

        work_load.append(workload_coeff*timeload_peak)
        base_load.append(baseload)


# ===== calculation of illumination load

illum_load = []

for d in range (0, 365):

    workday_day = workday[d*24]

    for h in range (0, 24):

        if use_ambient_data:  # if false, no need for the following checks

            h_idx = d*24 + h        # points to the hour of year [0..8759]

            if (tmy_data[1]['GHI'][h_idx] <= illum_ghi):
                if workday_day:
                    illum_coeff = illum_hour_wd[h] 
                else:
                    illum_coeff = illum_hour_hd[h] 
                load_il = illum_coeff*illum_peak
            else:
                load_il = 0
        else:
            load_il = 0
            
        illum_load.append(load_il)


# ===== calculation of heating load

heat_load = []
heat_coeff = heat_peak / (heat_tmax - heat_tmin)

for d in range (0, 365):

    for h in range (0, 24):

        if use_ambient_data:  # if false, no need for the following checks

            h_idx = d*24 + h        # points to the hour of year [0..8759]
            tdry = tmy_data[1]['Tdry'][h_idx]

            if (tdry <= heat_tmax):
                if (tdry < heat_tmin):
                    tdry = heat_tmin
                load_ht = int(heat_coeff*(heat_tmax-tdry))
            else:
                load_ht = 0
        else:
            load_ht = 0
            
        heat_load.append(load_ht)


# ===== calculation of cooling load

cool_load = []
cool_coeff = cool_peak / (cool_tmax - cool_tmin)

for d in range (0, 365):

    for h in range (0, 24):

        if use_ambient_data:  # if false, no need for the following checks

            h_idx = d*24 + h        # points to the hour of year [0..8759]
            tdry = tmy_data[1]['Tdry'][h_idx]

            if (tdry >= cool_tmin):
                if (tdry > cool_tmax):
                    tdry = cool_tmax
                load_cl = int(cool_coeff*(tdry-cool_tmin))
            else:
                load_cl = 0
        else:
            load_cl = 0
            
        cool_load.append(load_cl)


# ===== load total

total_load = []

for i in range (0, 8760):
    total_load.append(base_load[i] +
                      work_load[i] +
                      illum_load[i] +
                      heat_load[i] +
                      cool_load[i])



# ===== show graph with the different loads in totals per day

total_day = tmy.tmy_daily_total(total_load)
base_day = tmy.tmy_daily_total(base_load)
work_day = tmy.tmy_daily_total(work_load)
illum_day = tmy.tmy_daily_total(illum_load)
heat_day = tmy.tmy_daily_total(heat_load)
cool_day = tmy.tmy_daily_total(cool_load)

data_tuple = (total_day, base_day, work_day,
              illum_day, heat_day, cool_day)
par_tuple = ('total load', 'baseload', 'work load','illumination',
             'heating load','cooling load')

header_text = 'load profile for ' + country
if use_ambient_data:
    header_text = header_text + ', ' + city
param_text = 'load (Wh/day)'

tmy.tmy_yearplot_mult (data_tuple, par_tuple, header_text, param_text)


# ===== print results on shell terminal
#

print (header_text)
print ('total load MWh =' + str(int(sum(total_load)/1000000)))
print ('baseload MWh =' + str(int(sum(base_load)/1000000)))
print ('work load MWh =' + str(int(sum(work_load)/1000000)))
print ('illumination load MWh =' + str(int(sum(illum_load)/1000000)))
print ('heating load MWh =' + str(int(sum(heat_load)/1000000)))
print ('cooling load MWh =' + str(int(sum(cool_load)/1000000)))
print ('')


# ===== store data in csv file
#

# build pandas dataframe 'load_profile' from the list and column names

if use_ambient_data:
    ghi_list = tmy_data[1]['GHI']
    tdry_list = tmy_data[1]['Tdry']
else:
    ghi_list = [0] * 8760
    tdry_list = [0] * 8760

load_profile = pd.DataFrame({ 'month' : month,
                              'day' : day,
                              'hour' : hour,
                              'weekday' : weekday,
                              'workday' : workday,
                              'base_load' : base_load,
                              'work_load' : work_load,
                              'GHI' : ghi_list,
                              'illum_load' : illum_load,
                              'Tdry' : tdry_list,
                              'heat_load' : heat_load,
                              'cool_load' : cool_load,
                              'total_load' : total_load})


# open new file in write mode, write initial information as .csv
# SUM and MAX evaluations are carried out directly in the datasheet

filename1 = out_directory + out_filename
newfile = open (filename1,'w')

newfile.write('Load simulation for ,' +  country + ',' + city + '\n')
newfile.write('Simulation carried out on ,' +
              dt.datetime.today().strftime('%d-%b-%Y %H:%M') + '\n')
newfile.write('Total load (Wh),=SUM(M8:M8767)' +
              ',,,,baseload,work,,illumination,,heating,cooling,total\n')
newfile.write('Total load (MWh),=ROUND((B3/1000000);2)' +
              ',,,,=ROUND((SUM(F8:F8767)/1000000);2)' +
              ',=ROUND((SUM(G8:G8767)/1000000);2)' +
              ',,=ROUND((SUM(I8:I8767)/1000000);2)' +
              ',,=ROUND((SUM(K8:K8767)/1000000);2)' +
              ',=ROUND((SUM(L8:L8767)/1000000);2)' +
              ',=ROUND((SUM(M8:M8767)/1000000);2)\n')
newfile.write('Peak load (kW),=ROUND((MAX(M8:M8767)/1000);2)' +
              ',,,,=ROUND((MAX(F8:F8767)/1000);2)' +
              ',=ROUND((MAX(G8:G8767)/1000);2)' +
              ',,=ROUND((MAX(I8:I8767)/1000);2)' +
              ',,=ROUND((MAX(K8:K8767)/1000);2)' +
              ',=ROUND((MAX(L8:L8767)/1000);2)' +
              ',=ROUND((MAX(M8:M8767)/1000);2)\n')
newfile.write('\n')


# open output file in append mode
# write structured load_profile data as .csv with pandas function

with open(filename1, 'a') as newfile:
    load_profile.to_csv(newfile, index=False,
                        columns=['month','day','hour','weekday',
                                 'workday','base_load','work_load',
                                 'GHI','illum_load','Tdry',
                                 'heat_load','cool_load','total_load'])
newfile.close()

print ('file saved: ' + filename1)
print ('')
