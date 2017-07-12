"""
solpath_Cartesian_time_elev.py
=====
make Cartesian plot for solar time, elevation at location and day

developed with Python3.5, tested with Python2.7

input:
- year, integer
- month, integer
- day, integer
- latitude, float
- calc step, time step for the calculation in minutes, integer

output:
Cartesian graph with solar elevation as function of time

full hours are indicated on the graph as circles


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
import matplotlib.dates as mdates
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

    # check if sun above horizon, append data to lists
    if (elev > 0):
        time.append(time_ref)
        sol_elev.append(elev)

    time_ref = time_ref + time_step


# ===== display plot
#
# subplot call, open drawing canvas
plt.figure()
ax = plt.subplot(111)

# ===== plot time, elevation angle
plt.plot(time, sol_elev, 'b', linewidth=1.5)


# ===== complete the plot, add texts
plt.grid(True)

# set limits for y_axis
# get y coordinates after automatic scaling
ylim = plt.gca().get_ylim()     # get y coordinates after scaling
if (ylim[0] < 0):
    plt.ylim(0, ylim[1])    # y_min = 0, y_max as defined automatically

plt.xlabel('apparent solar time', size=10, family='sans-serif')
plt.ylabel('solar elevation angle', size=10, family='sans-serif')
plt.title('solar elevation at lat=' + str(latitude) + ' on ' + day_str,
          family='sans-serif', size=10)

# format x axis representation with hour, minute
#
formatter = mdates.DateFormatter('%H:%M')   
plt.gcf().axes[0].xaxis.set_major_formatter(formatter)  

plt.xticks(family='sans-serif',size=10)
plt.yticks(family='sans-serif',size=10)
  
plt.show()
plt.close()

