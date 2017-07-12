"""
plot_tmy_noontime.py
=====
plot the calculated noontime at a location from the TMY ghi data

developed with Python3.5, tested with Python2.7

from the ghi parameter in a TMY3 file find the time for the weighed
maximum on each day, plot the output. The constant time difference to
local noon depends on timezone and longitude. The variable time shift
depends on the equation of time correction.

input:
- directory, file for TMY dataset

output:
- plot of the noontime calculated from weighed GHI values over the
sunshine hours of each day for the full year


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

#tmyFileName = 'TMY_ITA_Bologna161400_(EPW).csv'     # Bologna
#tmyFileName = 'TMY_ITA_Bolzano160200_(EPW).csv'     # Bolzano
tmyFileName = 'TMY-EPW_ITA_Trieste161100_CONVERT.csv'     # Trieste


# ===== input directory
tmyDirectory = 'data-TMY/'


# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import solprim.tmyutility as tmy
import solprim.solartimeposition as stp



# ===== read data
tmy_data = tmy.tmy_readcsv(tmyDirectory + tmyFileName)

# show location metadata on terminal output
print (tmy_data[0])
print ('')

country = tmy_data[0]['Country']
city = tmy_data[0]['City']

# get data for noon average
noon_average = tmy.tmy_noontime_from_ghi(tmy_data[1]['GHI'])

noon_hour = stp.solar_time_HHMM(noon_average[1])


# display plot
text_head = (country + '_' + city +
             ' avg noon time from TMY data is ' +
             str(noon_average[1]) + ' [' + noon_hour + ']')
text_param = 'calculated noon time'
tmy.tmy_yearplot(noon_average[0], text_head, text_param)

