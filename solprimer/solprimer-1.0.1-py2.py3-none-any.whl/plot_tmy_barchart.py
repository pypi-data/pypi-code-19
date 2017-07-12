"""
plot_tmy_barchart.py
=====
plot monthly barchart of selected parameter from TMY dataset over the year

developed with Python3.5, tested with Python2.7

input:
- directory, file for TMY dataset
- parameter to plot, must be column name in TMY dataset/ pandas array,
string

output:
- barchart for the cumulated monthly or yearly value for the selected
parameter from TMY dataset


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

#tmyFileName = 'TMY-EPW_RUS_SaintPetersburg260630_CONVERT.csv'     # St.Petersburg
#tmyFileName = 'TMY-EPW_THA_Bangkok.484560_CONVERT.csv'     # Bangkok
tmyFileName = 'TMY-EPW_SGP_Singapore486980_CONVERT.csv'     # Singapore


# ===== input directory
tmyDirectory = 'data-TMY/'


# select parameter for monthly totals or averages
# remove comment sign '#' near the parameter to be plotted
# for non-cumulative values such as 'Tdry', 'RH', 'Pres' the daily average
# must be divided by 24 to obtain a meaningful hourly average

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

country = tmy_data[0]['Country']
city = tmy_data[0]['City']


# the function 'tmy_monthly_total()[0]' returns the totals per month
# 'tmy_monthly_total()[1]' returns the daily averages
mon_values = tmy.tmy_monthly_total(tmy_data[1][param])[1]


header_text = country + '_' + city + ' TMY monthly values for ' + param

yaxis_text = param + ' daily average [Wh/m2]'


# draw barchart
tmy.month_barchart(mon_values, header_text, yaxis_text)

