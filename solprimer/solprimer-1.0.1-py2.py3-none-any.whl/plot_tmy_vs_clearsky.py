"""
plot_tmy_vs_clearsky.py
=====
read TMY file in .csv format, plot year ghi compared with clearsky ghi

developed with Python3.5, tested with Python2.7

input:
- directory, file for TMY dataset
- parameter to plot, must be column name in TMY dataset/ pandas array
for GHI/ DNI/ DHI, string

output:
- plot for the parameter value over the year together with the clear-sky
ghi value over the year for the same latitude, height


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

#tmyFileName = 'TMY-EPW_ITA_Rome162420_CONVERT.csv'
#tmyFileName = 'TMY-EPW_ITA_Trieste161100_CONVERT.csv'   # Trieste
#tmyFileName = 'TMY-EPW_DEU_Berlin103840_CONVERT.csv'   # Berlin
#tmyFileName = 'TMY-EPW_RUS_SaintPetersburg260630_CONVERT.csv'
#tmyFileName = 'TMY_USA_AZ_Phoenix722780_(TYA)_CONVERT.csv'     # Phoenix
#tmyFileName = 'TMY_USA_AZ_YumaIntlAP722800_(TYA)_CONVERT.csv'     # Yuma
tmyFileName = 'TMY-EPW_ARE_Abu.Dhabi412170_CONVERT.csv'

# ===== input directory
tmyDirectory = 'data-TMY/'


# ===== select parameter to plot 
# remove comment sign '#' near the parameter to be plotted 
param = 'GHI'
#param = 'DNI'
#param = 'DHI'


# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import solprim.solartimeposition as stp
import solprim.tmyutility as tmy



# ===== read data
tmy_data = tmy.tmy_readcsv(tmyDirectory + tmyFileName)


# show location metadata on terminal output
print (tmy_data[0])
print ('')

latitude = tmy_data[0]['Latitude']
height = tmy_data[0]['Elevation']
country = tmy_data[0]['Country']
city = tmy_data[0]['City']

# ===== generate solar irradiation values for latitude
sol_rad = stp.clearsky_radiation(latitude, height)

ghi_list = sol_rad[0]
dni_list = sol_rad[1]
dhi_list = sol_rad[2]


# calculate daily totals
par1_day_total = tmy.tmy_daily_total(tmy_data[1][param])
par2_day_total = tmy.tmy_daily_total(ghi_list)


# ===== plot values from TMY, simulated clear-sky

par_1 = param + ' from TMY data'
par_2 = 'clearsky ' + param

header_text = (country + '_' + city +
               ' (Lat=' + str(latitude) + ', ' +
               ' height=' + str(height) + ' m) ' + param +
               ' from TMY vs clearsky')

param_text = 'solar irradiation daily total [Wh/m2 day]'


# plot function
tmy.tmy_yearplot_mult((par1_day_total, par2_day_total),
                      (par_1, par_2), header_text, param_text, 0)

                  
