"""
plot_tmy_heatmap.py
=====
read a TMY file, plot heatmap of selected parameter for day/  hour

developed with Python3.5, tested with Python2.7

input:
- directory, file for TMY dataset
- parameter to plot, must be column name in TMY dataset/ pandas array,
string

output:
- heatmap for the selected parameter hourly value from TMY dataset


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

#tmyFileName = 'TMY-EPW_SGP_Singapore486980_CONVERT.csv'     # Singapore
#tmyFileName = 'TMY-EPW_AUS_NSW_Sydney947680_CONVERT.csv'  # Sydney
tmyFileName = 'TMY-EPW_SWE_StockholmArlanda024600_CONVERT.csv'  # Stockholm
#tmyFileName = 'TMY-EPW_CHN_Xinjiang-Kashi517090_CONVERT.csv'  # Kashgar/Kashi



# ===== input directory
tmyDirectory = 'data-TMY/'

# ===== select parameter to plot on heatmap
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

country = tmy_data[0]['Country']
city = tmy_data[0]['City']

header_text = country + '_' + city + ' TMY heatmap for '  + param

# ===== generate heatmap
tmy.tmy_heatmap(tmy_data[1][param], header_text)


