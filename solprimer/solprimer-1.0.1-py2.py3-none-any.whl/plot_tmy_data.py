"""
plot_tmy_data.py
=====
read TMY file in .csv format, plot selected parameter over the year

developed with Python3.5, tested with Python2.7

input:
- directory, file for TMY dataset
- parameter to plot, must be column name in TMY dataset/ pandas array,
string

output:
- graph for value of the selected parameter from TMY dataset over the year
- graph for the daily average of the selected parameter over the year


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

#tmyFileName = 'TMY_RUS_SaintPetersburg260630_(EPW).csv'
#tmyFileName = 'TMY_CAN_NU_Resolute719240_(EPW).csv'
#tmyFileName = 'TMY-EPW_SGP_Singapore486980_CONVERT.csv'     # Singapore

#tmyFileName = 'TMY_USA_AZ_Phoenix722780_(TYA)_CONVERT.csv'     # Phoenix
#tmyFileName = 'TMY_USA_CA_SouthLakeTahoe725847_(TYA)_CONVERT.csv'     # South Lake Tahoe
#tmyFileName = 'TMY_USA_HI_HonoluluIntlAP911820_(TYA)_CONVERT.csv'     # Honolulu
tmyFileName = 'TMY_USA_NY-NewYork_JFK744860_(TYA)_CONVERT.csv'     # New York


# ===== input directory
tmyDirectory = 'data-TMY/'


# ===== select parameter to plot on graph
# remove comment sign '#' near the parameter to be plotted 
param = 'GHI'
#param = 'DNI'
#param = 'DHI'
#param = 'Tdry'
#param = 'RH'
#param = 'Pres'


# ===== end of manual data input ===============


# =================================
# ========== main script ==========
# =================================
#

import solprim.tmyutility as tmy


# ===== read data
tmy_data = tmy.tmy_readcsv(tmyDirectory + tmyFileName)


# show location metadata on terminal output
print (tmy_data[0])
print ('')


# plot selected hourly data for the whole year
plot_header = (tmy_data[0]['Country'] + '_' + tmy_data[0]['City'] +
               ' TMY data plot for ' + param)

text_param = 'hourly GHI value in W/m2'

tmy.tmy_yearplot (tmy_data[1][param], plot_header, text_param)


# plot daily total data for the whole year
day_total = tmy.tmy_daily_average(tmy_data[1][param])

text_param = 'GHI daily average in W/m2 '

tmy.tmy_yearplot (day_total, plot_header, text_param)

                  
