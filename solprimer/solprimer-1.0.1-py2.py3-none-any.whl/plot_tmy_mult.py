"""
plot_tmy_mult.py
=====
read TMY file in .csv format, plot multiple parameters over the year

developed with Python3.5, tested with Python2.7

input:
- directory, file for TMY dataset
- parameter(s) to plot, each must be column name in TMY dataset/ pandas
array, string

output:
- graph for the selected parameter yearly values from TMY dataset

the code can be changed with similar code to display more than
two parameters


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

tmyFileName = 'TMY-EPW_RUS_SaintPetersburg260630_CONVERT.csv'
#tmyFileName = 'TMY_CAN_NU_Resolute719240_(EPW).csv'
#tmyFileName = 'TMY_SGP_Singapore486980_(EPW).csv'

#tmyFileName = 'TMY_USA_AZ_Phoenix722780_(TYA)_CONVERT.csv'     # Phoenix
#tmyFileName = 'TMY_USA_HI_HonoluluIntlAP911820_(TYA)_CONVERT.csv'     # Honolulu

# ===== input directory
tmyDirectory = 'data-TMY/'


# ===== select parameter to plot on graph
# remove comment sign '#' near the parameter to be plotted 
param1 = 'GHI'
#param1 = 'DNI'
#param1 = 'DHI'
#param1 = 'Tdry'
#param1 = 'RH'
#param1 = 'Pres'

#param2 = 'GHI'
param2 = 'DNI'
#param2 = 'DHI'
#param2 = 'Tdry'
#param2 = 'RH'
#param2 = 'Pres'


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

country = tmy_data[0]['Country']
city = tmy_data[0]['City']


# ===== plot selected data for the whole year
plot_header = country + '_' + city + ' TMY data plot'

text_param = 'solar irradiation total [Wh/m^2 day]'

par1_day_total = tmy.tmy_daily_total(tmy_data[1][param1])
par2_day_total = tmy.tmy_daily_total(tmy_data[1][param2])

# plot function
tmy.tmy_yearplot_mult((par1_day_total, par2_day_total),
                      (param1, param2), plot_header, text_param)

                  
