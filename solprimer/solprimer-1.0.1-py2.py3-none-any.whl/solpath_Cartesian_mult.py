"""
solpath_Cartesian_mult.py
=====
make Cartesian solar azimuth, elevation plot over several months 

developed with Python3.5, tested with Python2.7

input:
- year, integer
- month_list, list for selected months in the year [1..12], integer
- day, integer
- latitude, float
- calc step, time step for the calculation in minutes, integer

output:
Cartesian plot for the indicated day at the selected months with solar
elevation as function of azimuth and indication of the hours
3, 6, 9, 12, 15, 18, 21

full hours are marked on the graph as circles


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
day_ref = 20
latitude = 60
calc_step = 5   # time step for calculation and plotting, minutes

# months to be included in the graph with colors, for consistent plot
month_list = (1, 2, 3, 4, 5, 6, 12)  
month_color = ('c', 'k', 'g', 'y', 'm', 'r', 'b')

# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import matplotlib.pyplot as plt
import datetime as dt
import math

import solprim.solartimeposition as stp


# ===== display plot
#
# subplot call, open drawing canvas
plt.figure()
ax = plt.subplot(111)

# iterate over selected months, build the lists for time, elevation
for m in range (0, len(month_list)):

    # the timestep minutes=5 is defined as timedelta with constructor
    time_step = dt.timedelta(minutes = calc_step)

    # date and time constructor, time_ref is used for calculations, updated
    # by timestep    
    time_ref = dt.datetime(year, month_list[m], day_ref)
    time_last = time_ref + dt.timedelta(hours=24)   # end iteration after 24h

    time = []   # time point as list to be filled
    sol_azim = []   # azimuth as list to be filled
    sol_elev = []   # elevation as list to be filled

    # get solar declination for the selected day, result in decimal degrees
    sol_decl = stp.solar_declination(stp.day_of_year(time_ref))

    # conversion to radians
    latitude_rad = math.radians(latitude)
    sol_decl_rad = math.radians(sol_decl)

    # ===== calculate values in list, then plot curve for current month
    # iterate over time, build lists for azimuth, elevation
    while (time_ref <= time_last):
        
        # calculate hour angle from time, convert to radians
        hra = stp.hour_angle_localtime(time_ref)
        hra_rad = math.radians(hra)
        
        # the function solar_azim_elev returns the solar position as tuple
        sol_pos = stp.solar_azim_elev(sol_decl_rad, hra_rad, latitude_rad)
        elev = sol_pos[0]      # elevation in degrees has index =[0]
        azim = sol_pos[1]      # azimuth in degrees has index =[1]

        # check if sun above horizon, append data to lists
        if (elev > 0):
            time.append(time_ref)
            sol_azim.append(azim)
            sol_elev.append(elev)

        time_ref = time_ref + time_step


    # plot azimuth, elevation angles
    # label is name of the month, obtained via strftime() method
    plt.plot(sol_azim, sol_elev, color=month_color[m], linewidth=1.0,
             label=time_ref.strftime('%b'))

        
    # ===== plot points for hours 3, 6, 9, 12, 15, 18, 21
    #
    # the timestep is defined as timedelta with constructor
    time_step = dt.timedelta(hours=3)

    # date and time constructor, time_ref is used for calculations,
    # updated
    time_ref = dt.datetime(year, month_list[m], day_ref)

    # calculate and plot single points for selected hours
    # time_last_rad, sol_decl_rad same as already defined
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
                     markeredgecolor=month_color[m], linewidth=0.5)

        time_ref = time_ref + time_step


# ===== complete the plot, add texts
plt.grid(True)

#plt.axis([0, 360, 0, 90])       # rescale x, y axis
plt.xlabel('solar azimuth angle', size=10, family='sans-serif')
plt.ylabel('solar elevation angle', size=10, family='sans-serif')
plt.title('solar elevation vs azimuth for day ' + str(day_ref) +
          ' in different months at lat=' + str(latitude),
          family='sans-serif', size=10)

plt.legend(loc=3, fontsize=8)   # loc=3 means legend lower left

xticks_count = [45, 90, 135, 180, 225, 270, 315] 
xticks_label = ['45', '90', '135', '180', '225', '270', '315'] 

plt.xticks(xticks_count, xticks_label)
plt.xticks(family='sans-serif',size=10)
plt.yticks(family='sans-serif',size=10)
  
plt.show()
plt.close()


