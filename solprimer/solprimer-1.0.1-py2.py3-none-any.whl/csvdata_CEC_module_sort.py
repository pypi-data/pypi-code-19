"""
csvdata_CEC_module_sort.py
=====
read modules from CEC_Modules dataset, calculate efficiency, sort and store 

developed with Python3.5, tested with Python2.7
*** does not work under Python2.7 because of pandas function
non-compatibility ***


input:
- filename including directory for a dataset in .csv format, string
the file is sourced from the 'SAM' software system

output:
- file with the module data with calculated efficiency and sorted
by decreasing efficiency value

databases for reference data
SAM database list https://sam.nrel.gov/libraries
and SAM system for download/installation


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

# ===== Script parameters, insert manually =====
#

# ===== input file
csv_filename = 'CEC_Modules.csv'    # CEC database [18102 x 21]

# ===== input directory
csv_directory = 'data-input/'

# ===== output file
out_filename = 'CEC_Modules_eta2.csv'

# ===== output directory
out_directory = 'data-output/'


# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import solprim.readcsvfile as csv


# ===== read data
df = csv.readcsvfile(csv_directory + csv_filename)

# ===== add columns for P_max, efficiency not in the original dataset

# add column 'P_max' for max power as product of Mpp current and voltage
# the value is rounded to two decimals
df = df.assign(P_max = round(df['I_mp_ref'] * df['V_mp_ref'], 2))

# add column 'eta' for max efficiency, equal to max_power / area A_c
# divided by 1000 (conversion W to kW), multiplied by 100 (scale to %)
df = df.assign(eta = round(df['P_max'] / (df['A_c']*10), 2))


# ===== sort by decreasing efficiency

# sort by decreasing efficiency values and increasing module name (alpha)
# the function 'sort_values' does not act at the same time on a column
# and the index, solve by copying index into a new column 'index_col'
# and then proceed with sorting
#
df['index_col'] = df.index

# ascenting=False refers to 'eta', ascending=True refers to 'index_col'
df = df.sort_values(by=['eta', 'index_col'], ascending=[False, True])

print (df.eta)


# ===== save data in new .csv file

# save sorted list as csv with module name (index), efficiency values,
# maximum power
# further columns can be added to the header for save

header = ['eta', 'P_max', 'PTC', 'Technology']

filename1 = out_directory + out_filename

with open(filename1, 'w') as newfile:
    df.to_csv(newfile, index=True, columns = header)

newfile.close()


print ('file saved:  ' + filename1)
print ('')

