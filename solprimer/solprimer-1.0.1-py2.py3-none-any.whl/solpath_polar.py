"""
solpath_polar.py
=====
make polar plot for solar azimuth, elevation at given location and day

developed with Python3.5, tested with Python2.7

input:
- year, integer
- month, integer
- day, integer
- latitude, float
- calc step, time step for the calculation in minutes, integer

output:
polar graph with solar elevation as function of azimuth and indication
of the hours 3, 6, 9, 12, 15, 18, 21

full hours are indicated on the graph as circles

the elevation is processed in decimal degrees, azimuth in radians, both
represented in degrees


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
year = 2017
month = 6
day = 23
latitude = 20
calc_step = 5   # time step for calculation and plotting, minutes


# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import matplotlib.pyplot as plt
import datetime as dt
import math

import solprim.solartimeposition as stp


# the timestep = 5 minutes is defined as timedelta with constructor
time_step = dt.timedelta(minutes = calc_step)

# date and time constructor, time_ref is used for calculations, updated
# by timestep
time_ref = dt.datetime(year, month, day)
time_last = time_ref + dt.timedelta(hours=24)    # iteration end after 24hr
day_str = time_ref.strftime('%Y-%m-%d')     # string with year-month-day

time = []   # time point as list to be filled
sol_azim = []   # azimuth as list to be filled
sol_elev = []   # elevation as list to be filled

# get solar declination for the selected day, result in decimal degrees
sol_decl = stp.solar_declination(stp.day_of_year(time_ref))

# conversion to radians
latitude_rad = math.radians(latitude)
sol_decl_rad = math.radians(sol_decl)

# iterate over time, build lists for time, elevation 
while (time_ref <= time_last):
    
    # calculate hour angle from time, convert to radians
    hra = stp.hour_angle_localtime(time_ref)
    hra_rad = math.radians(hra)
    
    # the function solar_azim_elev returns the solar position as tuple
    sol_pos = stp.solar_azim_elev(sol_decl_rad, hra_rad, latitude_rad)
    elev = sol_pos[0]      # elevation in degrees has index =[0]
    azim = sol_pos[3]      # azimuth in radians has index =[3]

    # check if sun above horizon, append data to lists
    if (elev > 0):
        time.append(time_ref)
        sol_elev.append(90-elev)   # elev value in degrees
        sol_azim.append(azim)    # plot function for angle requires radians

    time_ref = time_ref + time_step
    

# ===== display plot
#
# subplot call as polar plot, open drawing canvas
plt.figure()
ax = plt.subplot(111, projection='polar')

# the plot function expects rad
# but zero at plot center, inversion is necessary

# verify 'clean' parametrization in order to have input in degree (not rad), 
# see matplotlib doc Chap 11 Sec 1 p 424 "plotting how to"

ax.plot (sol_azim, sol_elev, color='b', linewidth=1.5)
ax.set_rmax(90)
ax.set_theta_zero_location('N')  # set 0 degrees to the top of the plot
ax.set_theta_direction(-1)       # switch to clockwise (path East to West)
ax.set_yticks(range(91, 0, -10))
yLabel = ['0', '', '', '30', '', '', '60', '', '', '90']
ax.set_yticklabels(yLabel)
           
ax.set_title('solar path at Lat= ' + str(latitude) +' on ' + day_str,
             va='bottom', size=10, family='sans-serif')

plt.show()
plt.close()

