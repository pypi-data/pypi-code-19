"""
convert_tya_csv.py
=====
convert TMY3 file in updated format to .csv TMY3 previous format

developed with Python3.5, tested with Python2.7

module to access function 'solprim_tmyconvert.convert_tya_to_csv'

input:
- filename with directory path, string

output:
- .csv file in TMY3 (previous format)
- metadata for the location, shown on Python shell display

the converted output file is saved in the same directory as the 
input file. It has the name of the original file with the addition
'_CONVERT' and file type '.csv'

TMY3 TYA files are found at
http://rredc.nrel.gov/solar/old_data/nsrdb/1991-2005/tmy3/

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

# ===== input file

#tmyFileName = 'TMY_USA_CA_SanFrancisco_IntlApt724940_(TYA).csv'     # San Francisco
#tmyFileName = 'TMY_USA_HI_HonoluluIntlAP911820_(TYA).csv'     # Honolulu
tmyFileName = 'TMY_USA_NY-NewYork_JFK744860_(TYA).csv'     # New York JFK


# ===== input directory
tmyDirectory = 'data-input/'


# ===== end of manual data input ===============


# =================================
# ========== main script ==========
# =================================
#

import solprim.tmyconvert as conv

# convert file, produce output file
loc_data = conv.convert_tya_to_csv(tmyDirectory + tmyFileName)


