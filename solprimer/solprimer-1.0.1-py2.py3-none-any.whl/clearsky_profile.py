"""
clearsky_profile.py
=====
tabulate and plot clear-sky radiation at given latitude, height

developed with Python3.5, tested with Python2.7

for a latitude [-90..90] and a location height over sea level generate
hourly lists for direct normal irradiation (dni), diffuse horizontal
irradiation (ghi), global horizontal irradiation (ghi) and hourly totals.
Save tables with hourly and daily values, make plot of hourly values.

input:
- latitude, float
- height, m over sea level, float

output:
- table in .csv format with
    - hour angle
    - solar azimuth, float
    - solar elevation, float
    - extraterrestrial radiation ETR  [W/m2]
    - air mass, float
    - am_factor, air mass factor, float
    - GHI, simulated global horizontal radiation GHI [W/m2], integer
    - DNI, simulated direct normal radiation DNI [W/m2], integer
    - DHI, simulated diffuse horizontal radiation DHI [W/m2], integer


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


# ===== Script parameters, insert manually =====
#
latitude = 30       # latitude in decimal degrees
height = 10       # elevation in m


# ===== output directory
out_directory = 'data-output/'


# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import pandas as pd

import solprim.solartimeposition as stp
import solprim.tmyutility as tmy

# ===== radiation profile
#
# call solprimer.solartimeposition function to generate solar
# irradiation values at indicated latitude, elevation
sol_rad = stp.clearsky_radiation(latitude, height)

ghi_list = sol_rad[0]
dni_list = sol_rad[1]
dhi_list = sol_rad[2]

hra_time_list = sol_rad[3]
sol_azim_list = sol_rad[4]
sol_elev_list = sol_rad[5]
sol_power_list = sol_rad[6]
air_mass_list = sol_rad[7]
am_fact_list = sol_rad[8]


# ===== save clear-sky profile data in new file with pandas functions
#

# make pandas data structure

data = pd.DataFrame({ 'HRA' : hra_time_list,
                      'azim (deg)' : sol_azim_list,
                      'elev (deg)' : sol_elev_list,
                      'ETR [W/m2]' : sol_power_list,
                      'air mass (am)' : air_mass_list,
                      'am factor' : am_fact_list,
                      'GHI [W/m2]' : ghi_list,
                      'DNI [W/m2]' : dni_list,
                      'DHI [W/m2]' : dhi_list })


# open output file in write mode
# print data structured as .csv with pandas function
filename1 = (out_directory + 'clearsky_radiation_LAT' +
             str(int(latitude)) + '_H' + str(int(height)) + '_hr.csv') 

with open(filename1, 'w') as newfile:
    data.to_csv(newfile, index=False,
                columns=['HRA','azim (deg)','elev (deg)', 'ETR [W/m2]',
                         'air mass (am)','am factor','DNI [W/m2]',
                         'GHI [W/m2]','DHI [W/m2]'])

newfile.close()

print ('file saved: ' + filename1)
print ('')


# ===== calculate and save ghi, dni, dhi totals 
#

# calculate daily totals
ghi_day = tmy.tmy_daily_total(ghi_list)
dni_day = tmy.tmy_daily_total(dni_list)
dhi_day = tmy.tmy_daily_total(dhi_list)

# make pandas data structure
data = pd.DataFrame({ 'ghi_day' : ghi_day,
                      'dni_day' : dni_day,
                      'dhi_day' : dhi_day })

# open output file in write mode
# print data structured as .csv with pandas function
filename1 = (out_directory + 'clearsky_radiation_LAT' +
             str(int(latitude)) + '_H' + str(int(height)) + '_day.csv')

with open(filename1, 'w') as newfile:
    data.to_csv(newfile, index=False,
                columns=['ghi_day','dni_day','dhi_day'])

newfile.close()

print ('file saved: ' + filename1)
print ('')


# ===== plot clear sky solar radiation, day average 

solar_rad = (ghi_day, dni_day, dhi_day)
solar_label = ('ghi', 'dni', 'dhi')

header_text = ('generated clear-sky solar irradiation for latitude = ' +
               str(int(latitude)) + ', height= ' +
               str(int(height)) + ' m')

param_text = 'solar irradiation component [Wh/m2 day]'

tmy.tmy_yearplot_mult(solar_rad, solar_label, header_text, param_text, 0)

