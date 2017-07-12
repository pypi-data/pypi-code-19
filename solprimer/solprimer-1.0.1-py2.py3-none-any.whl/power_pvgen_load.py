"""
power_pvgen_load.py
=====
solar PV system simulation with load

developed with Python3.5, tested with Python2.7

process steps
- read TMY file
- read hourly load data from .csv file
- read solar panel data (or use preset values)
- show location metafile
- calculate plane-of-array (POA) radiation for oriented panel
- calculate generated ac power from POA irradiation, temperature, and
- efficiency (loss) aspects
- simulate load coverage, storage, excessive generation, extra demand

input:
- directory, file for TMY dataset
- directory, name for output .csv file
- csv_directory, input directory for solar module dataset
- csv filename, input file for solar module dataset
- module_name, name for a PV module
- relevant system parameters, such as
    pvmod_number,  number of PV modules
    pvmod_limit,  POA threshold W/m2, no generation below this limit 
    sys_eff, total pv system generation & conversion efficiency
    storage_size, storage capacity in Wh
    storage_efficiency, storage efficiency (battery power loss)


PV module data is found in the 'CEC_Module' dataset or the 'Sandia module'
dataset

alternatively, relevant pv module parameters can be given explicitly
the read section for the solar module needs to be commented away

output:
.csv file with
- location metadata
- pv module and system data
- hourly values for ghi, dni, dhi, Tdry, POA irradiation, Tcell, 
  generated power (dc/ac), storage charge status, extra external demand,
  extra generation


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
# ===== TMY input file

#tmy_filename = 'TMY-EPW_ITA_Bologna161400_CONVERT.csv'   # Bologna
#tmy_filename = 'TMY-EPW_ITA_Bolzano160200_CONVERT.csv'   # Bolzano
#tmy_filename = 'TMY-EPW_RUS_SaintPetersburg260630_CONVERT.csv'

#tmy_filename = 'TMY_USA_HI_HonoluluIntlAP911820_(TYA)_CONVERT.csv'     # Honolulu
tmy_filename = 'TMY_USA_NY-NewYork_JFK744860_(TYA)_CONVERT.csv'     # New York
#tmy_filename = 'TMY-EPW_SGP_Singapore486980_CONVERT.csv'


# ===== input directory for TMY data
tmy_directory = 'data-TMY/'


# ===== input filename for load profile data
load_filename = 'load_profile_001.csv'


# ===== input directory for load profile data
load_directory = 'data-input/'


# ===== output file
out_filename = 'PVgen_load_simulation_001.csv'


# ===== output directory
out_directory = 'data-output/'



# ===== oriented array plane
array_azim = 180    # oriented plane azimuth, 180 is due south
array_tilt = 30    # oriented plane tilt over ground, degrees
#

# ===== system
pvmod_number = 1080   # number of PV modules
pvmod_limit = 50   # POA threshold W/m2, no generation below this limit 
sys_eff = 0.90    # total pv system generation & conversion efficiency
storage_size = 2800000  # Storage capacity in Wh
storage_efficiency = 1.0   # storage efficiency (battery power loss)
#

# ===== PV module data
#
module_name = 'manual parameter input'
pvmod_Pnom = 165    # power output at STC (nominal power)
pvmod_Tcoeff = -0.0045    # temp. coefficient (gamma) of Pnom (x%/C)
pvmod_noct = 45     # solar module NOCT
pvmod_area = 1.5    # area of the module in m2
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
    - pvmod_Tcoeff: temperature coefficient gamma (gamma), power change%
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



def storage_simulation (gen_list, load_list, storage_max=0,
                        storage_init=0, storage_efficiency=1.0):

    """
    input
    - gen_list, list with generation values in range [0..8759]
    - load_list, list with load values in range [0..8759]
    - storage_max, maximum storage capacity
    - storage_init, initial storage charge
    - storage_efficiency, applied to the value from gen_list before
    storage, float

    the values of gen_list and load_list must be in the same units
    (W, kW, MW)
    the values of storage_max and storage_init must be in the same units
    as gen_list and load_list per hour (Wh, kWh, MWh)

    returns
    - storage_state, list with the hourly storage content [0..8759] 
    - demand_state, list with the demand for external power [0..8759] 
    - excess_state, list with hourly power overproduction [0..8759]  

    """
    # storage_charge is the current charge of the power battery
    # storage_charge initialization
    storage_charge = storage_init
    
    if (storage_charge > storage_max):
        storage_charge = storage_max

    if (storage_efficiency > 1.0):
        storage_efficiency = 1.0

    storage_state = []      # initialize state lists
    demand_state = []
    excess_state = []

    for h in range (0, 8760):       # iterate over all hours
        
        power_gen = gen_list[h]
        power_load = load_list[h]

        gen_delta = power_gen - power_load

        if (gen_delta >= 0):

            # the efficiency coefficient <=1.0 is applied
            # to the excess power 'gen_delta' during storage
            
            if (storage_charge < storage_max):
                storage_charge = (storage_charge +
                                  gen_delta * storage_efficiency)
                gen_delta = 0
                
                if (storage_charge > storage_max):
                    gen_delta = (storage_charge-storage_max)
                    storage_charge = storage_max

            storage_state.append(storage_charge)
            demand_state.append(0)
            excess_state.append(gen_delta)

        else:

            if (storage_charge >= 0):
                storage_charge = storage_charge + gen_delta
                gen_delta = 0

                if (storage_charge < 0):
                    gen_delta = -storage_charge
                    storage_charge = 0

            storage_state.append(storage_charge)
            demand_state.append(gen_delta)
            excess_state.append(0)


    return (storage_state, demand_state, excess_state)



import pandas as pd
import datetime as dt

import solprim.tmyutility as tmy
import solprim.readcsvfile as csv



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



# ===== read file with load profile data
#
# open file in read mode
load_file = open(load_directory + load_filename, 'r')

# header=5 to skip over rows
# row=6 in the input file contains the data headers, row=[7..8766]
# the data
# column names are read from row=6 and allocated automatically

load_data = pd.read_csv(load_file, header=5) 
load_file.close()

load_list = load_data['total_load']


# ===== display PV, system parameters
#

array_power = int(pvmod_number*pvmod_Pnom)      # installed PV power W
array_size = round((pvmod_number*pvmod_area),1)      # total area m2

print ('===== system data')
print ('array azimuth=' + str(array_azim) +
       ',  array tilt=' + str(array_tilt) + '\n')
print ('PV module type = ' + module_name)
print ('P_STC (W) = ' + str(pvmod_Pnom))
print ('PTC (W) = ' + str(pvmod_PTC))
print ('NOCT =' + str(pvmod_noct))
print ('pvmod_Tcoeff =' + str(pvmod_Tcoeff))
print ('no of modules =' + str(pvmod_number))
print ('installed power/ nameplate dc rating (W) =' + str(array_power))
print ('module area (m2) =' + str(pvmod_area) + 
       '  array total area (m2) =' + str(array_size))
print ('')

load_total_mwh = round((sum(load_list)/1000000), 2)
storage_size_mwh = round((storage_size/1000000), 2)

# storage time as capacity/load, converted to days 
storage_time = round((storage_size_mwh*365/load_total_mwh), 2)

print ('Storage size (MWh) = ' + str(storage_size_mwh))
print ('Storage time at avg load (days) = ' + str(storage_time))
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



# ===== simulate system with generation, load, storage
#

storage_init = storage_size     # begin with fully loaded charge

simul_profile = storage_simulation (pvgen_list, load_list, storage_size,
                                    storage_init, storage_efficiency)
storage_list = simul_profile[0]
demand_list = simul_profile[1]
excess_list = simul_profile[2]


# ===== display totals on Python shell output device
# array_power is in W
# the storage capacity in days is calculated from the storage capacity
# divided by the average load
#

#storage_total = round((storage_size/1000000), 2)

pvgen_total_mwh = round((sum(pvgen_list)/1000000), 2)
demand_total_mwh = round((sum(demand_list)/1000000), 2)
excess_total_mwh = round((sum(excess_list)/1000000), 2)

print ('===== main simulation results')
print ('Total yearly generation (MWh) = ' + str(pvgen_total_mwh))
print ('Total load (MWh) = ' + str(load_total_mwh))
print ('Total external demand (MWh) = ' + str(demand_total_mwh))
print ('Total extra generation (MWh) = ' + str(excess_total_mwh))
print ('')


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
                               'PV_gen' : pvgen_list,
                               'load' : load_list,
                               'charge' : storage_list,
                               'demand' : demand_list,
                               'excess' : excess_list})


# open new file in write mode, write initial information as .csv
# SUM calculations are carried out directly in the datasheet

filename1 = out_directory + out_filename
newfile = open (filename1,'w')

newfile.write('PV generation for ,' +  country + ',' + city + '\n')
newfile.write('Simulation carried out on ,' +
              dt.datetime.today().strftime('%d-%b-%Y %H:%M') + '\n')
newfile.write('\n')
newfile.write('PV module type,' + module_name +
              ',,power:,W_STC,' + str(pvmod_Pnom) +  
              ',W_PTC,' + str(pvmod_PTC) +
              ',NOCT,'+ str(pvmod_noct) + '\n')
newfile.write('No. of modules,' + str(pvmod_number) +
              ',,tilt,'+ str(array_tilt) +
              ',azim,' + str(array_azim) + '\n')
newfile.write('Array total area (m2),' + str(array_size) + '\n')
newfile.write('Array peak power (W),' + str(array_power) + '\n')
newfile.write('Load peak (W),' + '=MAX(K15:K8774)\n')
newfile.write('Storage size (MWh),' + str(storage_size_mwh) + '\n')
newfile.write('Storage at avg load (days),' + str(storage_time) + '\n')
newfile.write('Total generation (MWh),' + str(pvgen_total_mwh) + '\n')

newfile.write('Total load (MWh),=ROUND((SUM(K15:K8774)/1000000);2)' +
              ',,Totals (MWh):,=ROUND((SUM(E15:E8774)/1000000);2)' +
              ',=ROUND((SUM(F15:F8774)/1000000);2)' +
              ',=ROUND((SUM(G15:G8774)/1000000);2)' +
              ',=ROUND((SUM(H15:H8774)/1000000);2)' +
              ',,=ROUND((SUM(J15:J8774)/1000000);2)' +
              ',=ROUND((SUM(K15:K8774)/1000000);2)' +
              ',,=ROUND((SUM(M15:M8774)/1000000);2)' +
              ',=ROUND((SUM(N15:N8774)/1000000);2)\n')

newfile.write('\n')
newfile.close()


# open output file in append mode
# write structured load_profile data as .csv with pandas function

with open(filename1, 'a') as newfile:
    pvgen_profile.to_csv(newfile, index=False,
                         columns=['month','day','hour','Tdry','GHI',
                                  'DNI','DHI','POA','Tcell','PV_gen',
                                  'load','charge','demand','excess'])
newfile.close()

print ('file saved: ' + filename1)
print ('')

