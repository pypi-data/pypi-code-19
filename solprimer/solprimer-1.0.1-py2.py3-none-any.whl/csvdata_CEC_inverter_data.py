"""
csvdata_CEC_inverter_data.py
=====
display all data for a solar inverter from the CEC_Inverters dataset

developed with Python3.5, tested with Python2.7


input:
- filename including directory for a dataset in .csv format, string
the file is sourced from the 'SAM' software system

- name of inverter contained in the dataset, string

output:
- full set of parameters for the indicated module

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

# ===== Script parameters, insert manually =====
#

# ===== input file
csv_filename = 'CEC_Inverters.csv'    # SAM database [3772 x 14]

# ===== input directory
csv_directory = 'data-input/'

# ===== inverter name
inverter = 'Solar_Power__YS_3000TL__240Vac__240V__CEC_2015_'

# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import pandas as pd

import solprim.readcsvfile as csv


# ===== read data
df = csv.readcsvfile(csv_directory + csv_filename)


# ===== display inverter data
print (df.loc[inverter])
print ('')

