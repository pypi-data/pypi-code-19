"""
csvdata_component_list.py
=====
display as text the index names of all items from a dataset

developed with Python3.5, tested with Python2.7


input:
- filename including directory for a dataset in .csv format, string
the file is sourced from the 'SAM' software system

output:
- textfile with index content of the dataset

databases for reference data
SAM database list https://sam.nrel.gov/libraries
and SAM system for download/installation

filename https://sam.nrel.gov/sites/default/files/
sam-library-sandia-modules-2015-6-30.csv

Python module based on the pvlib function 'pvlib.pvsystem.retrieve_sam'

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

#csv_filename = 'CEC_Inverters.csv'    # SAM database [3772 x 14]
#csv_filename = 'CEC_Modules.csv'    # SAM database, [18102 x 21]
csv_filename = 'Sandia_Modules.csv'   # Sandia database [523 x 42]


# ===== input directory
csv_directory = 'data-input/'


# ===== output directory
out_directory = 'data-output/'


# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import pandas as pd

import solprim.readcsvfile as csv


# ===== read data
df = csv.readcsvfile(csv_directory + csv_filename)


# by default, there is a 30 rows limit in the display printout 
# to override the limit, the pandas method 'set_option' should be used
# this method seems NOT to work, either with display or output file
#pd.set_option('display.max_rows', 50000) 

# the 'max_seq_items' method works for both display and output file
# the new limit must be set higher than the maximum number of items
# otherwise the older limit is not changed

pd.options.display.max_seq_items = 20000



# ===== save as txt file

# get original filename, add 'index', produce output file name
dot_ptr = csv_filename.find('.')
out_filename = csv_filename[0:dot_ptr] + '_index.txt'
filename1 = out_directory + out_filename

# data is stored as pandas
# file open in write mode
newfile = open(filename1,'w')

# iterate on index length, extract index, write all index items
for i in range (0, len(df.index)):
    newfile.write(df.index[i] + '\n')

# close the file
newfile.write('\n')
newfile.close()

print ('file saved: ' + filename1)
print ('')


