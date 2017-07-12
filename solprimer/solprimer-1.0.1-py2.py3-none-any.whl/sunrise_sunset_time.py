"""
sunrise_sunset_time.py
=====
list sunrise, sunset time for all days of the year

developed with Python3.5, tested with Python2.7
*** does not work under Python 2.7, because the datetime
object has no attribute 'timezone' ***

for a location identified by latitude and longitude generate and save
a list with the sunrise and sunset time for all days of the year


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
# reference data for Cardiff, Wales, UK
#
latitude = 51.5         # latitude, North is positive
longitude = -3.2         # longitude, East is positive
timezone = 0.0          # timezone, positive values are East (tz=1 is UTC+1)

# output directory for generated .csv file
out_directory = 'data-output/'

# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import datetime as dt
import math
import pandas as pd

import solprim.solartimeposition as stp


# build a datetime object with year, month, day, timezone
#
year = dt.datetime.today().year     # get current year from system
month = 1
day = 1


# in datetime format the timezone must be a timedelta with
# tz in minutes
tz = dt.timezone(dt.timedelta(minutes=timezone*60)) 

# date constructor
localdate = dt.datetime(year, month, day, tzinfo=tz)

# delta = 1 day in datetime format, to increase the date value in the
# iteration
one_day = dt.timedelta(days=1)

# lists for date, solar declination, sunrise and sunset time
# (apparent solar time), sunrise and sunset time (local time)
date = []
solar_decl = []
sunrise_sol_HHMM = []
sunset_sol_HHMM = []
sunrise_loc_HHMM = []
sunset_loc_HHMM = []

for d in range (0, 365):    #iterate over all days of the year

    sol_decl = stp.solar_declination(stp.day_of_year(localdate))

    # sunrise hour
    sr_hour = stp.sunrise_hour(sol_decl,latitude)

    # sunrise hour is a tuple
    sunrise_solar = sr_hour[1]
    sunset_solar = sr_hour[2]
    sunrise_flag = sr_hour[3]
    polar_day_flag = sr_hour[4]

    if (sunrise_flag):

        # sunrise, sunset time (solar) converted to hh:mm
        sunrise_sol_HHMM.append(stp.solar_time_HHMM(sunrise_solar))
        sunset_sol_HHMM.append(stp.solar_time_HHMM(sunset_solar))

        # sunrise, sunset local (official) time as Python datetime
        # objects, returned by 'local_time_from_solar'
        # the function 'local_time_from_solar' carries out the
        # corrections for longitude, Equation of Time
        sunrise_local = stp.local_time_from_solar(sunrise_solar,
                                                  localdate, longitude)
        sunset_local = stp.local_time_from_solar(sunset_solar,
                                                 localdate, longitude)

        # conversion to string format with datetime.strftime method 
        sunrise_loc_HHMM.append(sunrise_local.strftime('%H:%M'))
        sunset_loc_HHMM.append(sunset_local.strftime('%H:%M'))

    else:
        if (polar_day_flag):
            reason = 'Pol_day'
        else:
            reason = 'Pol_night'

        sunrise_sol_HHMM.append(reason)
        sunset_sol_HHMM.append(reason)
        sunrise_loc_HHMM.append(reason)
        sunset_loc_HHMM.append(reason)

    date.append(localdate.strftime('%Y-%m-%d'))
    solar_decl.append(sol_decl)

    localdate = localdate + one_day  


# ===== save results in .csv file
# procedure for saving tabular data:
# 1. produce lists with the 'append()' method, done above
# 2. build a pandas dataframe from the single lists
# 3. use pandas function 'to_csv()' to produce a .csv file

# build the dataframe
data = pd.DataFrame({ 'Date' : date,
                      'Solar_decl' : solar_decl,
                      'Sunrise_solar' : sunrise_sol_HHMM,
                      'Sunset_solar' : sunset_sol_HHMM,
                      'Sunrise_local' : sunrise_loc_HHMM,
                      'Sunset_local' : sunset_loc_HHMM })

# save the file
filename = ('sunrise_sunset_hour_LAT' + str(int(latitude)) + '_LON' +
            str(int(longitude)) + '_' + str(tz) + '.csv')

filename1 = out_directory + filename

with open(filename1, 'w') as newfile:
    data.to_csv(newfile, index=False,
                columns=['Date','Solar_decl','Sunrise_solar',
                         'Sunset_solar', 'Sunrise_local',
                         'Sunset_local'])

newfile.close()

# print message on Python shell 
print ('file saved: ' + filename1)
print ('')


