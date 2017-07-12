"""
plot_poa_heatmap.py
=====
from TMY data calculate yearly POA irradiation, plot azim/tilt heatmap

developed with Python3.5, tested with Python2.7


input:
- directory, file for TMY dataset
- azimuth angle range for the flat collection module [0..360],
integer/float
- tilt angle for the flat collection module [0..90], integer/float


Attention! The complete iteration over 181 azimuth x 91 tilt angles 
for the range Azimuth = 90-270, Tilt = 0-90 (16,471 runs) requires 
approx 1h50min. For this reason the POA is calculated only at major 
intervals, intermediate values are interpolated.

Simulation with interval = 30 takes 11 sec 
Simulation with interval = 15 takes 32 sec 
Simulation with interval = 10 takes 70-75 sec 
Simulation with interval = 5 takes 226 sec (3min 46sec)
Simulation with interval = 3 takes 697 sec (11min 7sec)

The simulations with large intervals, 15/ 30 degrees, brings a very 
rough picture. Simulations with incremental steps of 5 or 10 degrees
produce a good-quality picture, but require some minutes' time. 

The script builds a 2D-array for the POA calculated for the full range of 
azimuth, tilt angles with step=1. All values are initially filled with 0's. 
The actual POA result is calculated only at major intervals (value to be
set manually), the intermediate POA values are interpolated


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
# ===== to ensure backward compatibility with Python2.7
#
from __future__ import division



# ===== Script parameters, insert manually =====
#

# ===== input file

tmyFileName = 'TMY-EPW_ITA_Bologna161400_CONVERT.csv'     # Bologna
#tmyFileName = 'TMY-EPW_ITA_Bolzano160200_CONVERT.csv'     # Bolzano
#tmyFileName = 'TMY-EPW_DEU_Berlin103840_CONVERT.csv'     # Berlin
#tmyFileName = 'TMY_USA_AZ_Phoenix722780_(TYA)_CONVERT.csv'     # Phoenix
#tmyFileName = 'TMY_USA_CA_SanFrancisco_IntlApt724940_(TYA)_CONVERT.csv'     # San Francisco



# ===== input directory
tmyDirectory = 'data-TMY/'


# ===== plane orientation

# oriented plane azimuth, orientation 180 is due south
# indicate range for orientation and tilt, in degrees
plane_azim_from = 90
plane_azim_to = 270
plane_azim_step = 10

plane_tilt_from = 0
plane_tilt_to = 90
plane_tilt_step = 10


# ===== end of manual data input ===============


# =================================
# ========== main script ==========
# =================================
#

import numpy as np
import pandas as pd

import time

import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.colorbar as col

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


# ===== variable initialization, lists
poa_azim = []     # plane orientation
poa_tilt = []     # plane tilt
poa_yield = []     # energy yield at orientation, tilt


# ===== 1. calculate plane-of-array (poa) values at 'step' points
#

# time check, measure execution speed
start_time = time.time()

for pl_az in range (plane_azim_from, plane_azim_to+1):

    for pl_tl in range (plane_tilt_from, plane_tilt_to+1):

        # for azimuth and tilt at 'step' calculate POA hourly values
        # with a call to the tmy 'plane_of_array' function
        # otherwise take a preliminary value =0, it will be used
        # to fill the numpy array and as placeholder before interpolation

        if ((pl_az%plane_azim_step == 0) and
            (pl_tl%plane_tilt_step == 0)):
            poa_interm = tmy.tmy_plane_of_array (dni_list, dhi_list,
                                                 latitude, longitude,
                                                 timezone, pl_az, pl_tl)
            poa_list = poa_interm[0]
            poa_total = int(sum(poa_list)/1000)

        else:
            poa_total = 0

        poa_azim.append(pl_az)
        poa_tilt.append(pl_tl)
        poa_yield.append(poa_total)


# end time check, display execution speed
print ('main calculation execution speed, sec =' + str(time.time()-start_time))



# ===== 2. build the numpy bi-dimensional array
#

# determine numpy array size on x, y axis
x_len = int(plane_azim_to - plane_azim_from + 1)
y_len = int(plane_tilt_to - plane_tilt_from + 1)

# build a numpy array, initial values all=0
t_array = np.zeros((y_len, x_len))    



# ===== 3. interpolate values for increasing tilt angles in numpy array
#

# time check, measure execution speed
start_time = time.time()

for o in range (0, x_len, plane_azim_step):
    for t in range (0, y_len-plane_tilt_step, plane_tilt_step):

        base_idx = o*y_len + t  # list pointer

        en_delta = (poa_yield[base_idx+plane_tilt_step]-
                    poa_yield[base_idx])/plane_tilt_step

        for i in range (0, plane_tilt_step):
            t_array[t+i, o] = poa_yield[base_idx] + i*en_delta
            
    t_array[y_len-1, o] = poa_yield[base_idx + plane_tilt_step]


print ('numpy interpolation #1, run time = ' +
       str(time.time()-start_time))


# ===== 4. interpolate values for azimuth/orientation in numpy array

# time check, measure execution speed
start_time = time.time()

for o in range (0, x_len-plane_azim_step, plane_azim_step):
    for t in range (0, y_len):

        en_delta = (t_array[t, o+plane_azim_step] -
                    t_array[t, o])/plane_azim_step

        for i in range (1, plane_azim_step):
            t_array[t, o+i] = t_array[t, o] + i*en_delta

print ('numpy interpolation #2, run time = ' +
       str(time.time()-start_time))



# ===== 5. produce and display heatmap

# time check, measure execution speed
start_time = time.time()


header_text = ('flat panel yearly energy yield in ' + country +
               '_' + city + ', Lat=' + str(int(latitude)))


# colormaps are shown in
# http://scipy.github.io/old-wiki/pages/Cookbook/Matplotlib/Show_colormaps
# from here is selected the color range in 'cmap=' in the plt.imshow call


# figure and subplot call 
plt.figure()
ax = plt.subplot(111)


# set the min-max color range automatically
plt.imshow(t_array, cmap='jet', extent=[0,180,0,90], aspect='auto',
           origin='lower')

# set the min-max color range manually with vmin, vmax
# plt.imshow(t_array, cmap='jet', extent=[0,365,0,24], aspect=12,
#           origin='lower', vmin=0, vmax=1300)


plt.colorbar(shrink=1.0)

plt.grid(True)
plt.title(header_text, family='sans-serif', size=10)

plt.xlabel('azimuth angle')
plt.ylabel('tilt angle')


plt.xticks([0, 45, 90, 135, 180],
       ['90', '135', '180', '225', '270'], size=10)
plt.yticks([0, 30, 60, 90], ['0','30','60','90'], size=10)


# end time check, display execution speed
print ('figure processing, run time = ' +
       str(time.time()-start_time))


# display result
plt.show()
plt.close()


