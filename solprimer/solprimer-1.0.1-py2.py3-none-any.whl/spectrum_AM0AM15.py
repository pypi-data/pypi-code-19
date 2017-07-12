"""
spectrum_AM0AM15.py
=====
read from spreadsheet (Excel format) values for AM0, AM1.5, plot graph

developed with Python3.5, tested with Python2.7

Data source for spreadsheet with solar radiation data:
www.pveducation.org/sites/default/files/PVCDROM/Appendices/AM0AM1_5.xls

Alternative data source:
http://rredc.nrel.gov/solar/spectra/am1.5/astmg173/ASTMG173.xls


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
# ===== input file, directory

directory = 'data-input/'
filename = 'AM0AM1_5.xls'


# =================================
# ========== main script ==========
# =================================
#

import matplotlib.pyplot as plt
import pandas as pd


# ===== read Excel file with AM0, AM1.5 solar radiation data

# the pandas 'read_excel' function requires names for all columns
# with data even when this data is not read and processed
# in the following they are called 'unnamed1/2/3'
#
# if the file 'ASTMG173.xls' from the NREL website is used, the column
# names in the pandas read_excel function need to be changed accordingly

solar_rad = pd.read_excel(directory + filename,
                          sheetname='Spectra',skiprows=1,
                          names=['um','ETR','global_tilt','direct',
                                 'unnamed1','unnamed2','unnamed3'])


# ===== plot the graph
#
# open canvas for drawing
plt.figure()
plt.subplot(111)


# plot AM0 radiation 'ETR' over the wavelength 'um'
plt.plot(solar_rad['um'], solar_rad['ETR'], 'b',
         linewidth=1, label = 'AM0')

# plot AM1.5 radiation 'global tilt' over the wavelength 'um'
plt.plot(solar_rad['um'], solar_rad['global_tilt'], 'r',
         linewidth=0.5, label = 'AM1.5 global tilt')

# plot direct radiation 'direct' over the wavelength 'um'
plt.plot(solar_rad['um'], solar_rad['direct'], 'g',
         linewidth=0.5, label = 'AM1.5 direct')


# format and plot graph
plt.axis([200, 2500, 0, 2.3]) # rescale x, y axis
plt.xlabel('wavelength nm', family='sans-serif', size=10)
plt.ylabel('radiation intensity W/ m2 nanometer',
           family='sans-serif', size=10)

plt.title('solar radiation spectrum', family='sans-serif', size=10)
plt.legend()


plt.show()
plt.close()

