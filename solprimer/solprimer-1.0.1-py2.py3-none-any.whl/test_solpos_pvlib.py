"""
test_solpos_pvlib.py
=====
compare outcome of solar primer, pvlib solar position algorithms

developed and tested with Python3.5, not tested with Python2.7


this test procedure requires the installation of pvlib
pvlib is the NREL library of solar PV functions for Python
information on http://pvlib-python.readthedocs.io 

input:
- latitude, float
- longitude, float

output:
- table in .csv format with
    - date and time
    - solar declination, float
    - equation of time, float
    - solar time, float
    - azimuth, float
    - elevation, float

computed by pvlib and the 'solprim_solartimeposition' functions

PVLIB-PYTHON information, including Copyright information, is found at
https://pvlib-python.readthedocs.io/en/latest/index.html
https://pypi.python.org/pypi/pvlib/


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

# ===== Script parameters, insert manually =====
#
year = 2017
latitude = 23
longitude = 45

# ===== output file and directory
out_directory = 'data-output/'
out_filename = ('solpos_LAT' + str(latitude) +
                '_LON' + str(longitude) + '.csv')


# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import datetime as dt
import time
import math
import pandas as pd

import solprim.solartimeposition as stp

import pvlib


# ===== display input data
print ("lat =", latitude, "lon =", longitude)

# ===== initialize data

month = 1
day = 1
hour = 0
minute = 0

# time check, measure execution speed
start_time = time.time()

# ===== pvlib, prepare solar position list 
# date and time constructor
localtime = dt.datetime(year, month, day, hour, minute)

# timestep = one hour
timestep = dt.timedelta(hours = 1)

pvlib_datetime = []
pvlib_eot = []
pvlib_azim = []
pvlib_elev = []


while (localtime.year == year):
    
    # call to pvlib solpos function

    solpos = pvlib.solarposition.get_solarposition(localtime,
                                                   latitude,
                                                   longitude)
    azim = round(solpos.azimuth[0], 2)
    elev = round(solpos.elevation[0], 2)
    eot = round(solpos.equation_of_time[0], 2)
    
    pvlib_datetime.append(localtime)
    pvlib_eot.append(eot)
    pvlib_azim.append(azim)
    pvlib_elev.append(elev)

    localtime = localtime + timestep


# end time check, display execution speed
end_time = time.time()
print ('pvlib execution speed, sec =' + str(end_time-start_time))


# ===== solprimer.solartimeposition, prepare solar position list 

# time check, measure execution speed
start_time = time.time()

stp_year = []
stp_month = []
stp_day = []
stp_hour = []
stp_soldecl = []
stp_eot = []
stp_azim = []
stp_elev = []
stp_eot_azim = []
stp_eot_elev = []



# iterate over all days, hours

for d in range (1, 366):

    # get solar declination, result in decimal degrees
    sol_decl = stp.solar_declination(d)

    # conversion to radians
    latitude_rad = math.radians(latitude)
    sol_decl_rad = math.radians(sol_decl)

    # get equation of time, result in decimal minutes
    eot = stp.equation_of_time(d)


    for h in range (0, 24):

        # calculate hour angle from solar time corrected for eot,
        # longitude

        hra = stp.hour_angle_decimal(h, eot, longitude)
        hra_rad = math.radians(hra)
        
        # solar_azim_elev returns the solar position as a tuple
        # arguments need to be passed in radians
        sol_pos = stp.solar_azim_elev(sol_decl_rad, hra_rad,
                                      latitude_rad)

        elev = sol_pos[0]      # elevation in degrees has index =[0]
        azim = sol_pos[1]      # azimuth in degrees has index =[1]

        stp_day.append(d)
        stp_hour.append(h)
        stp_eot.append(eot)
        stp_azim.append(azim)
        stp_elev.append(elev)


# end time check, display execution speed
end_time = time.time()
print ('solartimeposition execution speed, sec =' +
       str(end_time-start_time))


# ===== save data table from the lists and column names in .csv format  

# use pandas functions, build pandas dataframe 'solpos_test'
solpos_test = pd.DataFrame({ 'pvlib_date' : pvlib_datetime,
                             'pvlib_eot' : pvlib_eot,
                             'pvlib_azim' : pvlib_azim,
                             'pvlib_elev' : pvlib_elev,
                             'stp_day' : stp_day,
                             'stp_hour' : stp_hour,
                             'stp_eot' : stp_eot,
                             'stp_azim' : stp_azim,
                             'stp_elev' : stp_elev
                             })

# open new file in write mode
# write structured load_profile data as .csv with pandas function

filename1 = out_directory + out_filename

with open(filename1, 'w') as newfile:
    solpos_test.to_csv(newfile, index=False,
                       columns=['pvlib_date','pvlib_eot','pvlib_azim',
                                'pvlib_elev','stp_day','stp_hour',
                                'stp_eot','stp_azim','stp_elev'
                                ])

newfile.close()

print ('file saved: ' + filename1)
print ('')




