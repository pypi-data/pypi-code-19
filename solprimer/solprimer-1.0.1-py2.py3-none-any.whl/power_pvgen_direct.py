"""
power_pvgen_direct.py
=====
simulate solar power array operation (feed-in) for given TMY input data

developed with Python3.5, tested with Python2.7

process steps
- read TMY file
- read solar panel data (or use preset values)
- show location metadata
- calculate plane-of-array (POA) radiation for oriented panel
- calculate generated dc power from POA irradiation, temperature
- calculate net ac power with efficiency (loss) factor on dc

input:
- directory, file for TMY dataset
- directory, name for output .csv file
- csv_directory, input directory for solar module dataset
- csv filename, input file for solar module dataset
- module_name, name for a PV module

PV module data is found in the 'CEC_Module' dataset or the 'Sandia module'
dataset

alternatively, relevant pv module parameters can be given explicitly
the read section for the solar module needs to be commented away

output:
- barchart with monthly values for average Plane-of-Array irradiance
[kWh/m2 day]
- barchart with total generated power per month [MWh]
.csv file with
- location metadata
- pv module and system data
- hourly values for ghi, dni, dhi, Tdry, POA irradiation, Tcell,
generated dc/ac power after estimated losses

Attention! when reading the .csv file into the spreadsheet program set
only the comma ',' as separator. The semicolon ';' is not a field separator,
but an input to the function processor.


databases for reference data
SAM database list https://sam.nrel.gov/libraries
and SAM system for download/installation

filename https://sam.nrel.gov/sites/default/files/
sam-library-sandia-modules-2015-6-30.csv

Important Notice =====
The System Advisory Model (SAM) software has been developed by NREL
For copyright and other information see https://sam.nrel.gov/


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

# ===== input TMY file

#tmy_filename = 'TMY-EPW_ITA_Bologna161400_CONVERT.csv'   # Bologna
#tmy_filename = 'TMY-EPW_ITA_Bolzano160200_CONVERT.csv'   # Bolzano
#tmy_filename = 'TMY-EPW_RUS_SaintPetersburg260630_CONVERT.csv'
#tmy_filename = 'TMY_RUS_Yakutsk249590_(EPW).csv'

#tmy_filename = 'TMY_USA_AZ_Phoenix722780_(TYA)_CONVERT.csv'
tmy_filename = 'TMY_USA_NY-NewYork_JFK744860_(TYA)_CONVERT.csv'
#tmy_filename = 'TMY_CAN_NU_Resolute719240_(EPW).csv'
#tmy_filename = 'TMY-EPW_SGP_Singapore486980_CONVERT.csv'

#tmy_filename = 'TMY-EPW_THA_Bangkok.484560_CONVERT.csv'   # Bangkok
#tmy_filename = 'TMY-EPW_CHN_Shanghai583620_CONVERT.csv'   # Shanghai
#tmy_filename = 'TMY-EPW_DEU_Munich108660_CONVERT.csv'   # Munchen
#tmy_filename = 'TMY-EPW_BRA_RioDeJaneiro837550_CONVERT.csv'   # Rio de Janeiro


# ===== input directory for TMY data
tmy_directory = 'data-TMY/'


# ===== output file
out_filename = 'PVgen_simulation_001.csv'


# ===== output directory
out_directory = 'data-output/'


# ===== output color for the barchart
# b: blue, g: green, r: red, c: cyan, m: magenta,y: yellow, k: black,
# w: white, '0.70': gray shade

bar_color = 'b'


# ===== oriented array plane
array_azim = 180    # oriented plane azimuth, 180 is due south
array_tilt = 38    # oriented plane tilt over ground, degrees
#                     
# ===== system
pvmod_number = 12   # number of PV modules
pvmod_limit = 10   # POA threshold W/m2, no generation below this limit
sys_eff = 0.90    # total pv system generation & conversion efficiency
#

# ===== PV module data
#
module_name = 'manual parameter input'
pvmod_Pnom = 165    # power output at STC (nominal power)
pvmod_Tcoeff = -0.0045    # temp. coefficient (gamma) of Pnom (x%/C)
pvmod_noct = 45     # solar module NOCT
pvmod_area = 1.5    # # area of the module in m2
pvmod_PTC = None    # for display output if module data is not read
                    # from dataset; no manual input required

# ===== end of manual input data =====



# comment away this section when module
# parameters are given manually
#
# =============================================
# ===== read from PV dataset ==================
# =============================================
#
# ===== input file for solar module dataset
csv_filename = 'CEC_Modules.csv'    # SAM database [18102 x 21]

# ===== input directory for solar module dataset
csv_directory = 'data-input/'

# ===== module name
# All non-alphanumeric characters in dataset need to be substituted with
# underscore '_'
#module_name = '1Soltech_1STH_215_P'
#module_name = '1Soltech_1STH_350_WH'
#module_name = 'iTek_iT_230'
#module_name = 'Green_Energy_Technology_GET_340A'
module_name = 'SunPower_SPR_X21_335_BLK'


# ===== read module data from dataset
import solprim.readcsvfile as csv
df = csv.readcsvfile(csv_directory + csv_filename)

# power output at STC (nominal power, nameplate dc rating)
pvmod_Pnom = int(df.loc[module_name].I_mp_ref *
                 df.loc[module_name].V_mp_ref)
#
# PTC power output (for display only)
pvmod_PTC = df.loc[module_name].PTC
#
# temp. coefficient (gamma) of Pnom (x%/C)
pvmod_Tcoeff = round((df.loc[module_name].gamma_r *
                      pvmod_Pnom / 100), 5)
#
# NOCT for the solar cell
pvmod_noct = df.loc[module_name].T_NOCT
#
# module size
pvmod_area = df.loc[module_name].A_c
#
# ===== end read from PV module dataset =====
#
# =============================================
# ===== read from PV dataset, section end =====
# =============================================
#




# =================================
# ========== main script ==========
# =================================
#


def pvmodule_output_power (irrad, tdry, pvmod_Pnom, pvmod_Tcoeff,
                           pvmod_noct):
    """
    calculate the output power of a solar module depending on its
    parameters, solar irradiation, ambient temperature. At the beginning
    is calculated the cell operation temperature, from the temperature
    follows the power gain/loss with respect to STC nominal and the
    actual power output as function of the irradiation
    
    input
    - irrad: solar irradiation (W/m2), integer/float
    - tdry: ambient temperature (degrees C), float
    - pvmod_Pnom: max power output at STC (W), float
    - pvmod_Tcoeff: temperature coefficient gamma, power change%
    at STC Treference =25 C compared to Pmax (x%/C), float
    - pvmod_noct: NOCT reference temperature, to estimate cell work
    temperature at given irradiation, ambient temperature, float

    returns
    - power_out, actual power generated by the module (W), float
    - cell_temp, cell estimated work temperature (degrees C), float 

    """

    # fixed reference values
    Tref_stc = 25       # STC reference temperature = 25 C
    Tref_noct = 20      # NOCT reference temperature = 20 C

    # cell temperature from Tdry, NOCT
    cell_temp = tdry + round(((pvmod_noct-Tref_noct)*irrad/800), 1)
    
    # nominal power output at the calculated cell temperature
    power_nom = pvmod_Pnom + pvmod_Tcoeff*(cell_temp-Tref_stc)

    # output power at current irradiation value (STC reference =1000 W)
    power_out = power_nom * irrad/1000


    return power_out, cell_temp



import pandas as pd
import datetime as dt

import textwrap         # necessary to print long string to file

import solprim.tmyutility as tmy


# ===== read TMY data
tmy_data = tmy.tmy_readcsv(tmy_directory + tmy_filename)

# tmy_data[0] is the pandas dataframe with location metadata 
# show on terminal output
print (tmy_data[0])
print ('')

country = tmy_data[0]['Country']
city = tmy_data[0]['City']
latitude = tmy_data[0]['Latitude']
longitude = tmy_data[0]['Longitude']
timezone = tmy_data[0]['Time Zone']


# tmy_data[1] is the pandas dataframe with index [0..8760] and columns
# for TMY parameters

dni_list = tmy_data[1]['DNI']
dhi_list = tmy_data[1]['DHI']
tdry_list = tmy_data[1]['Tdry']



# ===== display PV, system parameters
#

array_power = int(pvmod_number*pvmod_Pnom)      # installed PV power W
array_size = round((pvmod_number*pvmod_area),1)      # total area m2

print ('===== system data')
print ('array azimuth=' + str(array_azim) +
       '  array tilt=' + str(array_tilt))
print ('PV module type = ' + module_name)
print ('P_STC (W) = ' + str(pvmod_Pnom))
print ('PTC (W) = ' + str(pvmod_PTC))
print ('NOCT =' + str(pvmod_noct))
print ('pvmod_Tcoeff =' + str(pvmod_Tcoeff))
print ('no of modules =' + str(pvmod_number))
print ('installed power/ nameplate dc rating (W) =' + str(array_power))
print ('module area (m2) =' + str(pvmod_area) +
       '   array total area (m2) =' + str(array_size))
print ('')


# ===== calculate Plane Of Array values in W/m2
poa_list = tmy.tmy_plane_of_array(dni_list, dhi_list, latitude,
                                  longitude, timezone,
                                  array_azim, array_tilt)[0]

# ===== display yearly, day average insolation data, calculated POA
# data is per m2 and refers to location

ghi_year_kwh = round((sum(tmy_data[1]['GHI'])/1000), 1)
dni_year_kwh = round((sum(tmy_data[1]['DNI'])/1000), 1)
dhi_year_kwh = round((sum(tmy_data[1]['DHI'])/1000), 1)
ghi_day_kwh = round((ghi_year_kwh / 365), 2)
dni_day_kwh = round((dni_year_kwh / 365), 2)
dhi_day_kwh = round((dhi_year_kwh / 365), 2)

poa_year_kwh = round((sum(poa_list)/1000), 1)
poa_day_kwh = round((poa_year_kwh / 365), 2)

print ('===== location-specific TMY insolation data')
print ('GHI year total per m2 =' + str(ghi_year_kwh) + ' kWh/m2' +
       '     per day =' + str(ghi_day_kwh) + ' kWh/m2')
print ('DNI year total per m2 =' + str(dni_year_kwh) + ' kWh/m2' +
       '     per day =' + str(dni_day_kwh) + ' kWh/m2')
print ('DHI year total per m2 =' + str(dhi_year_kwh) + ' kWh/m2' +
       '     per day =' + str(dhi_day_kwh) + ' kWh/m2')
print ('POA year total per m2 =' + str(poa_year_kwh) + ' kWh/m2' +
       '     per day =' + str(poa_day_kwh) + ' kWh/m2')
print ('')


# ===== from POA calculate system power output for all hours

pvgen_list = []     # power generation, list to be filled
tcell_list = []     # cell temperature, list to be filled


for h in range (0, 8760):
    poa_power = poa_list[h]
    if (poa_power >= pvmod_limit):
        pvmod_output = pvmodule_output_power(poa_power, tdry_list[h],
                                             pvmod_Pnom, pvmod_Tcoeff,
                                             pvmod_noct)

        # mod_power is the output power per module, multiply per
        # number of modules, efficiency to get total net array output
        mod_power = pvmod_output[0]
        sys_power = round((mod_power*pvmod_number*sys_eff), 0)
        cell_temp = pvmod_output[1]
    else:
        sys_power = 0
        cell_temp = tdry_list[h]

    pvgen_list.append(sys_power)
    tcell_list.append(cell_temp)


# ===== display totals on Python shell output device
# array_power is in W
pvgen_total_w = round(sum(pvgen_list), 1)
pvgen_total_mwh = round((pvgen_total_w/1000000), 2)
poa_array_mwh = round((poa_year_kwh*array_size/1000), 2)
kwh_per_kwp = round((pvgen_total_w/array_power), 2) 
kwh_per_poa = round((pvgen_total_mwh/(poa_array_mwh)), 2)

print ('===== main simulation results')
print ('Total yearly generation (MWh) = ' + str(pvgen_total_mwh))
print ('Total yearly POA insolation (MWh) = ' + str(poa_array_mwh))
print ('PV generation coeff. kWh/kWp =' + str(kwh_per_kwp))
print ('PV generation / total POA insol =' + str(kwh_per_poa))
print ('')



# ===== display results in barcharts
#

# ===== calculate monthly POA average per day, plot barchart

# mon_stat[1] is daily average per month (actual month length), list
# mon_stat[3] is the yearly average

mon_stat = tmy.tmy_monthly_total(poa_list)

poa_month = mon_stat[1]

poa_month = [x/1000 for x in poa_month]     # convert Wh to kWh    

header_text = (country + '_' + city + ', POA irradiance daily average')

param_text = 'Average Plane-of-Array irradiance [kWh/m2 day]'

box_text = ('array tilt ' + str(array_tilt) +
            ', az ' + str(array_azim) + '\n' +
            'year avg =' + str(round((mon_stat[3]/1000),2)) + ' kWh')

tmy.month_barchart(poa_month, header_text, param_text, bar_color,
                   box_text)


# ===== calculate monthly generation totals and plot barchart
#

pvgen_month = tmy.tmy_monthly_total(pvgen_list)[0]

pvgen_month = [x/1000000 for x in pvgen_month]       # convert Wh to MWh

header_text = (country + '_' + city + ' yearly PV power generation')

param_text = 'Total generated power per month [MWh]'

box_text = ('array tilt ' + str(array_tilt) +
            ', az ' + str(array_azim) +
            ', P = ' + str(array_power) + ' W''\n' +
            'year total =' + str(pvgen_total_mwh) + ' MWh' + '\n' +
            'kWh/kWp =' + str(kwh_per_kwp))

tmy.month_barchart(pvgen_month, header_text, param_text, bar_color,
                   box_text)



# ===== save data table from the lists and column names in .csv format  

# round values for poa_list
for i in range (0, 8760):
    poa_list[i] = round(poa_list[i], 0)

# use pandas functions, build pandas dataframe 'pvgen_profile'
pvgen_profile = pd.DataFrame({ 'month' : tmy_data[1]['Month'],
                               'day' : tmy_data[1]['Day'],
                               'hour' : tmy_data[1]['Hour'],
                               'Tdry' : tdry_list,
                               'GHI' : tmy_data[1]['GHI'],
                               'DNI' : dni_list,
                               'DHI' : dhi_list,
                               'POA' : poa_list,
                               'Tcell' : tcell_list,
                               'PV_gen' : pvgen_list })


# open new file in write mode, write initial information as .csv
# SUM evaluations are carried out directly in the datasheet


filename1 = out_directory + out_filename
newfile = open (filename1,'w')

newfile.write('PV generation for ,' +  country + ',' + city + '\n')
newfile.write('Simulation carried out on ,' +
              dt.datetime.today().strftime('%d-%b-%Y %H:%M') + '\n')
newfile.write('Array tilt,' + str(array_tilt) + '\n')
newfile.write('Array azimuth,' + str(array_azim) + '\n')
newfile.write('Module name,' + module_name + '\n')
newfile.write('No. of modules,' + str(pvmod_number) + '\n')
newfile.write('Module STC power (W),' + str(pvmod_Pnom) + '\n')
newfile.write('Array peak power (W),' + str(array_power) + '\n')

newfile.write('Total generation (MWh),' +
              '=ROUND((SUM(J12:J8771)/1000000);2)' +
              ',,,=ROUND((SUM(E12:E8771)/1000000);2)' +
              ',=ROUND((SUM(F12:F8771)/1000000);2)' +
              ',=ROUND((SUM(G12:G8771)/1000000);2)' +
              ',=ROUND((SUM(H12:H8771)/1000000);2)' +
              ',,=ROUND((SUM(J12:J8771)/1000000);2)\n\n')

newfile.close()


# open output file in append mode
# write structured load_profile data as .csv with pandas function

with open(filename1, 'a') as newfile:
    pvgen_profile.to_csv(newfile, index=False,
                         columns=['month','day','hour','Tdry','GHI',
                                  'DNI','DHI','POA','Tcell','PV_gen'])
newfile.close()

print ('file saved: ' + filename1)


