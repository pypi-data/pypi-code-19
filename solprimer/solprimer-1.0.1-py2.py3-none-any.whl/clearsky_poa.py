"""
clearsky_poa.py
=====
hourly irradiation on oriented panel, insolation totals

developed with Python3.5, tested with Python2.7


input:
- latitude, float
- height, m over sea level, float
- plane_azim, azimuth angle for the flat-plane orientation, float
- plane_tilt_angle, list with the flat-plane tilt angles, float

output:
- plot of the clear-sky radiation daily total yield for a full year
over an oriented surface


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
latitude = 40       # latitude in decimal degrees
height = 10         # height over sea level, meter
plane_azim = 180    # oriented plane azimuth, 180 is due south
plane_tilt_list = [0, 20, 40, 60]

# ===== end of manual data input ===============



# =================================
# ========== main script ==========
# =================================
#

import solprim.solartimeposition as stp
import solprim.tmyutility as tmy


# ===== variable initialization, lists
poa_outcome = []
poa_label = []

longitude = 0
timezone = 0

# ===== clear-sky radiation at latitude
sol_rad = stp.clearsky_radiation(latitude, height)
dni_list = sol_rad[1]
dhi_list = sol_rad[2]

# ===== compute clear-sky plane-of-array at different tilt angles
for i in range (0, len(plane_tilt_list)):
    plane_tilt = plane_tilt_list[i]
    poa_list = tmy.tmy_plane_of_array(dni_list, dhi_list, latitude,
                                      longitude, timezone, plane_azim,
                                      plane_tilt)[0]

    poa_day_list = tmy.tmy_daily_total(poa_list)

    poa_outcome.append(poa_day_list)
    poa_label.append('Tilt =' + str(plane_tilt))


# ===== display graph 

header_text = ('clear-sky plane of array irradiation ' +
               'for latitude= ' + str(int(latitude)) +
               ', height= ' + str(int(height)) + ' m')

param_text = 'daily total solar irradiation [Wh/m2]'

tmy.tmy_yearplot_mult(poa_outcome, poa_label, header_text, param_text, 0)

