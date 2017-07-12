"""
plot_poa_barchart.py
=====
from TMY data calculate POA total monthly radiation, plot barchart  

developed with Python3.5, tested with Python2.7

input:
- directory, file for TMY dataset
- azimuth angle for the flat collection module [0..360], integer/float
- tilt angle for the flat collection module [0..90], integer/float

output:
- barchart for the Plane-of-Array (POA) collected monthly radiation


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

# ===== input file

#tmyFileName = 'TMY-EPW_ITA_Bologna161400_CONVERT.csv'     # Bologna
#tmyFileName = 'TMY-EPW_ITA_Bolzano160200_CONVERT.csv'     # Bolzano
#tmyFileName = 'TMY-EPW_DEU_Berlin103840_CONVERT.csv'     # Berlin
#tmyFileName = 'TMY_USA_AZ_Phoenix722780_(TYA)_CONVERT.csv'     # Phoenix
#tmyFileName = 'TMY_USA_CA_SanFrancisco_IntlApt724940_(TYA)_CONVERT.csv'     # San Francisco

tmyFileName = 'TMY-EPW_THA_Bangkok.484560_CONVERT.csv'     # Bangkok



# ===== input directory
tmyDirectory = 'data-TMY/'

# ===== plane orientation
# oriented plane azimuth, 180 is due south
plane_azim = 180    

# oriented plane tilt over ground, degrees
plane_tilt = 15    



# ===== end of manual data input ===============


# =================================
# ========== main script ==========
# =================================
#

import pandas as pd

import solprim.tmyutility as tmy


# ===== read data
tmy_data = tmy.tmy_readcsv(tmyDirectory + tmyFileName)


# show location metadata on terminal output
print (tmy_data[0])
print ('')


latitude = tmy_data[0]['Latitude']
longitude = tmy_data[0]['Longitude']
timezone = tmy_data[0]['Time Zone']
country = tmy_data[0]['Country']
city = tmy_data[0]['City']

dni_list = tmy_data[1]['DNI']
dhi_list = tmy_data[1]['DHI']


# ===== call to main function, calculate POA hourly values
poa_yield = tmy.tmy_plane_of_array(dni_list, dhi_list, latitude,
                                   longitude, timezone, plane_azim,
                                   plane_tilt)
poa_list = poa_yield[0]
dir_list = poa_yield[1]
dif_list = poa_yield[2]
    

print('Tilt =' + str(plane_tilt) +
      ' POA total=' + str(int(sum(poa_list)/1000)) +
      ' Beam total=' + str(int(sum(dir_list)/1000)) +
      ' Diff total=' + str(int(sum(dif_list)/1000)))
print ('')


# ===== plot the barchart

header_text = ('poa irradiation for ' + country + '_' + city +
               ' (Lat =' + str(int(latitude)) + '), plane tilt =' +
               str(plane_tilt) + '')

poa_list_month = tmy.tmy_monthly_total(poa_list)[0]

for i in range (0, 12):
    poa_list_month[i] = int(poa_list_month[i]/1000)


param_text = 'poa monthly irradiation [kWh/m2]'

tmy.month_barchart (poa_list_month, header_text, param_text)




