"""
solpath_Cartesian_azim_elev.py
=====
make Cartesian plot for solar azimuth, elevation at location and day

developed with Python3.5, tested with Python2.7

input:
- year, integer
- month, integer
- day, integer
- latitude, float
- calc step, time step for the calculation in minutes, integer

output:
- Cartesian graph with solar elevation as function of azimuth and
indications of the hours 3, 6, 9, 12, 15, 18, 21. The full hours are
indicated on the graph as circles


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
month = 5
day = 23
latitude = 50
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
time_last = time_ref + dt.timedelta(hours=24)   # end iteration after 24h
day_str = time_ref.strftime('%Y-%m-%d')     # string with year-month-day

time = []   # time point as list to be filled
sol_azim = []   # azimuth as list to be filled
sol_elev = []   # elevation as list to be filled

# get solar declination for the selected day, result in decimal degrees
sol_decl = stp.solar_declination(stp.day_of_year(time_ref))

# conversion to radians
latitude_rad = math.radians(latitude)
sol_decl_rad = math.radians(sol_decl)

# iterate over time, build the lists for azimuth, elevation 
while (time_ref <= time_last):

    # calculate hour angle from time, convert to radians
    hra = stp.hour_angle_localtime(time_ref)
    hra_rad = math.radians(hra)
    
    # the function solar_azim_elev returns the solar position as a tuple
    sol_pos = stp.solar_azim_elev(sol_decl_rad, hra_rad, latitude_rad)
    elev = sol_pos[0]      # elevation in degrees has index =[0]
    azim = sol_pos[1]      # azimuth in degrees has index =[1]

    # check if the sun is above the horizon, append data to lists
    if (elev > 0):
        time.append(time_ref)
        sol_azim.append(azim)
        sol_elev.append(elev)

    time_ref = time_ref + time_step


# ===== display plot
#
# subplot call, open drawing canvas
plt.figure()
ax = plt.subplot(111)

# ===== plot azimuth, elevation angles
plt.plot(sol_azim, sol_elev, 'r', linewidth=1.5)

# ===== generate and plot points for each full hour
# the timestep = 1 hour is defined as timedelta with constructor
time_step = dt.timedelta(hours=1)

# date and time constructor, time_ref is used for calculations, updated
time_ref = dt.datetime(year, month, day)

# time_last, sol_decl, latitude same as defined earlier

while (time_ref <= time_last):

    # calculate hour angle from time
    hra = stp.hour_angle_localtime(time_ref)
    hra_rad = math.radians(hra)
    
    # the function solar_azim_elev returns a tuple
    sol_pos = stp.solar_azim_elev(sol_decl_rad, hra_rad, latitude_rad)
    elev = sol_pos[0]      # elevation in degrees has index =[0]
    azim = sol_pos[1]      # azimuth in degrees has index =[1]

    # check if sun above horizon, plot point for selected month, hour
    # use empty circles as markers
    if (elev > 0):
        ax.plot (azim, elev, 'o', markerfacecolor='none',
                 markeredgecolor='r',linewidth=0.5)

    time_ref = time_ref + time_step


# ===== complete the plot, add texts
plt.grid(True)

# set limits for y_axis
# get y coordinates after automatic scaling, set Y-axis starting point =0
ylim = plt.gca().get_ylim()     # get y coordinates after scaling
plt.ylim(0, ylim[1])    # y_min = 0, y_max as defined automatically


plt.xlabel('solar azimuth angle', size=10, family='sans-serif')
plt.ylabel('solar elevation angle', size=10, family='sans-serif')
plt.title('solar elevation at lat=' + str(latitude) + ' on ' + day_str,
          family='sans-serif', size=10)

xticks_count = [45, 90, 135, 180, 225, 270, 315] 
xticks_label = ['45', '90', '135', '180', '225', '270', '315'] 

plt.xticks(xticks_count, xticks_label)
plt.xticks(family='sans-serif',size=10)
plt.yticks(family='sans-serif',size=10)
  
plt.show()
plt.close()

