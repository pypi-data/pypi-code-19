"""
spectrum_blackbody.py
=====
calculate and plot Planck radiation profile and solar spectrum AM0, AM1.5 

developed with Python3.5, tested with Python2.7


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
temp = 5777     # temperature, Kelvin
wlen0 = 0.3     # wavelength plot begin (micrometers)
wlen1 = 3.0    # wavelength plot end (micrometers)
steps = 120     # number of steps to calculate function

# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import matplotlib.pyplot as plt

import solprim.solarradiation as sr


# get Planck distribution profile
# the function returns a tuple with wavelengths in range [wlen0..wlen1]
# and radiation intensity
planck_distr = sr.planck_distribution(temp, wlen0, wlen1, steps)


# ===== plot the graph
#
# open canvas for drawing
plt.figure()
plt.subplot(111)

# ===== plot Planck radiation spectrum
plt.plot(planck_distr[0], planck_distr[1], 'r',
         linewidth=2, label = 'Planck')


# ===== read and plot AM0 solar radiation spectrum
solar_AM0 = sr.solar_spectrum_table_AM0()
plt.plot(solar_AM0[0], solar_AM0[1], 'b',
         linewidth=0.5, label = 'AM0')

# ===== read and plot AM1.5 solar radiation spectrum
solar_AM15 = sr.solar_spectrum_table_AM15()
plt.plot(solar_AM15[0], solar_AM15[1], 'g',
         linewidth=0.5, label = 'AM1.5')

# ===== format and plot overall graph
plt.axis([0.0, wlen1, 0, 2300]) # rescale x, y axis
plt.xlabel('wavelength um')
plt.ylabel('radiation intensity W/ m2 micrometer')

plt.title('Planck blackbody radiation spectrum for T= ' +
          str(temp) + ' K', size=10)
plt.legend()


plt.show()
plt.close()

