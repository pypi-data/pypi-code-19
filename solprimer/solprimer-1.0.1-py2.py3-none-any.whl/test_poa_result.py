"""
test_poa_result.py
=====
from TMY data calculate the hourly plane-of-array yield, save result

developed with Python3.5, tested with Python2.7

read TMY3 file, from DNI, DHI data and calculated solar position
find hourly irradiation on oriented surface (POA), store in a csv table

input:
- directory, file for TMY dataset
- output directory for the generated file
- azimuth angle for the flat collection module [0..360], integer/float
- tilt angle for the flat collection module [0..90], integer/float

output:
- file, spreadsheet (.csv format) for the calculated Plane-of-Array (POA)
radiation in the direct, diffuse, and total components and for input data
from TMY file


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
#tmyFileName = 'TMY_USA_AZ_Phoenix722780_(TYA)_CONVERT.csv'     # Phoenix
#tmyFileName = 'TMY_USA_CA_SanFrancisco_IntlApt724940_(TYA)_CONVERT.csv' # San Francisco
tmyFileName = 'TMY_USA_HI_HonoluluIntlAP911820_(TYA)_CONVERT.csv' # Honolulu

#tmyFileName = 'TMY-EPW_THA_Bangkok.484560_CONVERT.csv'     # Bangkok
#tmyFileName = 'TMY-EPW_SGP_Singapore486980_CONVERT.csv'     # Singapore


# ===== input directory
tmyDirectory = 'data-TMY/'

# ===== output directory
outDirectory = 'data-output/'


# ===== plane orientation
plane_azim = 180    # oriented plane azimuth, 180 is due south
plane_tilt = 38    # oriented plane tilt over ground, degrees


# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import pandas as pd
import time

import solprim.tmyutility as tmy



# ===== read data
tmy_data = tmy.tmy_readcsv(tmyDirectory + tmyFileName)

# show location metadata on terminal output
print (tmy_data[0])
print ('')

print ('plane azimuth =' + str(plane_azim) +
       '   plane tilt =' + str(plane_tilt))
print ('')

latitude = tmy_data[0]['Latitude']
longitude = tmy_data[0]['Longitude']
timezone = tmy_data[0]['Time Zone']
country = tmy_data[0]['Country']
city = tmy_data[0]['City']


dni_list = tmy_data[1]['DNI']
dhi_list = tmy_data[1]['DHI']


# ===== call to main function, get list with POA hourly values

# ===== time check, measure execution speed
start_time = time.time()


poa_test = tmy.tmy_plane_of_array(dni_list, dhi_list, latitude,
                                  longitude, timezone, plane_azim,
                                  plane_tilt)

poa_list = poa_test[0]
dir_list = poa_test[1]
dif_list = poa_test[2]
incid_list = poa_test[3]


# ===== end time check, display execution speed
end_time = time.time()
print ('tmy_plane_of_array execution speed sec =' +
       str(end_time-start_time))
print ('')


# save POA and other TMY data in new file

data = pd.DataFrame({ 'Year' : tmy_data[1]['Year'],
                      'Month' : tmy_data[1]['Month'],
                      'Day' : tmy_data[1]['Day'],
                      'Hour' : tmy_data[1]['Hour'],
                      'Incid' : incid_list,
                      'GHI' : tmy_data[1]['GHI'],
                      'DNI' : dni_list,
                      'DHI' : dhi_list,
                      'POA_dir' : dir_list,
                      'POA_dif' : dif_list,
                      'POA_total' : poa_list
                        })

# ===== open output file in write mode
# add data structured as .csv with pandas function

# the output file has the name of the original file
# with addition '_POA' and file type '.csv'
filename1 = (outDirectory + tmyFileName[8:-16] +
             '_poa_A' + str(int(plane_azim)) +
             '_T' + str(int(plane_tilt)) + '.csv') 

with open(filename1, 'w') as newfile:
    data.to_csv(newfile, index=False,
                columns=['Year','Month','Day','Hour',
                         'Incid','GHI','DNI','DHI',
                         'POA_dir','POA_dif','POA_total'])
newfile.close()

print ('file saved: ' + filename1)
print ('')


