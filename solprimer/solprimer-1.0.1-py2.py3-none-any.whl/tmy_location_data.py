"""
tmy_location_data.py
=====
read csv TMY3 file ('previous' format), display parameters

developed with Python3.5, tested with Python2.7

input:
- directory, file for TMY dataset
- ghi threshold value for the count of days with sufficient solar
irradiation [W/m2 day], integer
- indoor reference and outdoor threshold values for the calculation
of heating, cooling degree-days (hdd, cdd)

output:
- list of the key indicators about a location, including the number
of days with insufficient solar radiation (from the given threshold value)
and the heating. cooling degree-days (hdd, cdd)


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

#tmyFileName = 'TMY-EPW_ITA_Bologna161400_CONVERT.csv'     # Bologna
#tmyFileName = 'TMY-EPW_ITA_Bolzano160200_CONVERT.csv'     # Bolzano
tmyFileName = 'tmy_era_46.461_1_CONVERT.csv'     # PVGIS file


#tmyFileName = 'TMY-EPW_DEU_Berlin103840_CONVERT.csv'     # Berlin
#tmyFileName = 'TMY_USA_HI_HonoluluIntlAP911820_(TYA)_CONVERT.csv'   # Honolulu JFK
#tmyFileName = 'TMY-EPW_CAN_NU_Resolute719240_CONVERT.csv'     # CAN, Resolute

#tmyFileName = 'TMY_USA_HI_HonoluluIntlAP911820_(TYA)_CONVERT.csv'   # Honolulu

#tmyFileName = 'TMY-EPW_SGP_Singapore486980_CONVERT.csv'     # Singapore


# ===== input directory
tmyDirectory = 'data-TMY/'


# ghi threshold limit, to count low insolation days
ghi_threshold = 2000

# heating degree days, cooling degree days
hdd_threshold=13
hdd_ref=18

cdd_threshold=26
cdd_ref=24


# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import solprim.tmyutility as tmy


# ===== read data
tmy_data = tmy.tmy_readcsv(tmyDirectory+tmyFileName)


# show location metadata on terminal output
print (tmy_data[0])
print ('')


# show data for Tdry
print ('Tdry min =' + str(round(min(tmy_data[1]['Tdry']),1)) +
       ' max =' + str(round(max(tmy_data[1]['Tdry']),1)) +
       ' avg =' + str(round(sum(tmy_data[1]['Tdry']/8760),1)) +
       '  all degC')

print ('')

# show heating, cooling degree days

degree_days = tmy.tmy_hdd_cdd(tmy_data[1]['Tdry'],
                              hdd_threshold, hdd_ref,
                              cdd_threshold, cdd_ref)

print ('heating degree days =' + str(degree_days[0]))

print ('cooling degree days =' + str(degree_days[1]))

print ('')

# show maximum number of consecutive days with ghi < threshold
# 

day_count = tmy.tmy_low_ghi_days(tmy_data[1].GHI, ghi_threshold)

print ('number of consecutive days with ghi <' + str(ghi_threshold) +
       'Wh =' + str(day_count[0]))

print ('number of total days with ghi <' + str(ghi_threshold) +
       'Wh =' + str(day_count[1]))

print ('')


# show solar irradiation (GHI, DNI, DHI) statistical data 

param_list = ['GHI','DNI','DHI']

print ('specific irradiation values per m2')
print ('')

for i in range (len(param_list)):
    param = param_list[i]
    sol_stat = tmy.tmy_irradiation_stats(tmy_data[1][param])

    print ('key indicators about ' + param)

    print ('    maximum hourly irrad (Wh) =' + str(sol_stat[0]))
    print ('    maximum daily irrad (Wh) =' + str(sol_stat[1]) +
           ' on day =' + str(sol_stat[2]))
    print ('    year total insolation (kWh) =' + str(sol_stat[3]))
    print ('    day avg irradiation (Wh) =' +  str(sol_stat[4]))
    print ('')



