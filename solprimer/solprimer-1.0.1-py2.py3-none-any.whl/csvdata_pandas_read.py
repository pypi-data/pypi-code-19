"""
csvdata_pandas_read.py
=====
read csv database, return pandas dataframe

developed with Python3.5, tested with Python2.7


input:
- filename including directory for a dataset in .csv format, string
the file is sourced from the 'SAM' software system

output:
- pandas dataframe for the full dataset


databases for reference data
SAM database list https://sam.nrel.gov/libraries
and SAM system for download/installation

csv files are found in the SAM libraries folder

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
csv_filename = 'CEC_Modules.csv'    # SAM database, [18102 x 21]
#csv_filename = 'Sandia_Modules.csv'   # Sandia database [523 x 42]

# ===== input directory
csv_directory = 'data-input/'

# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import pandas as pd

import solprim.readcsvfile as csv


# ===== read data
df = csv.readcsvfile(csv_directory + csv_filename)

print (df)
print ('')



