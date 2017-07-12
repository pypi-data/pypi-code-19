"""
convert_epw_csv.py
=====
convert EPW TMY file to .csv TMY3 "previous" format

developed with Python3.5, tested with Python2.7

module to access function 'solprim_tmyconvert.convert_epw_to_csv'

input:
- filename with directory path, string

output:
- .csv file in TMY3 (previous format)
- metadata for the location, displayed on Python shell terminal

the converted output file is saved in the same directory as the 
input file. It has the name of the original file with the addition
'_CONVERT' and file type '.csv'

EPW files are found at https://energyplus.net/weather


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

#tmyFileName = 'TMY-EPW_ITA_Bologna161400.epw'     # Bologna
#tmyFileName = 'TMY-EPW_ITA_Bolzano160200.epw'     # Bolzano
#tmyFileName = 'TMY-EPW_DEU_Berlin103840.epw'     # Berlin
tmyFileName = 'TMY-EPW_RUS_SaintPetersburg260630.epw'     # St.Petersburg
#tmyFileName = 'TMY-EPW_SGP_Singapore486980.epw'     # Singapore


# ===== input directory
tmyDirectory = 'data-input/'


# ===== end of manual data input ===============


# =================================
# ========== main script ==========
# =================================
#

import solprim.tmyconvert as conv


# convert file, produce output file
loc_data = conv.convert_epw_to_csv(tmyDirectory + tmyFileName)




