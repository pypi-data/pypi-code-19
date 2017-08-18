#!/usr/bin/python
# Copyright (c) 2015.
#

# Author(s):
#   Martin Raspaud <martin.raspaud@smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#

"""Generate plots of the next passes
"""
import argparse
from datetime import datetime, timedelta
from trollsched.schedule import read_config
from trollsched.satpass import get_next_passes
from trollsched.boundary import AreaDefBoundary

def read_xml(xml_file):
    raise NotImplementedError

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--lon", help="Longitude, degrees east", type=float)
    parser.add_argument("--lat", help="Latitude, degrees north", type=float)
    parser.add_argument("--alt", help="Altitude, km", type=float)

    parser.add_argument("config", help="configuration file to use",
                        default=None)
    parser.add_argument("-o", "--output-dir",
                        help="where to put generated plots",
                        default="/tmp/plots")
    parser.add_argument("-x", "--xml",
                        help="xml file to use as schedule",
                        default=None)

    opts = parser.parse_args()

    if opts.xml:
        passes, start_time, end_time = read_xml(opts.xml)
    else:
        passes = []
        start_time = datetime.utcnow()
        end_time = start_time + timedelta(hours=24)

    coords, scores, station, area, forward, start = read_config(opts.config)
    satellites = scores.keys()
    allpasses = get_next_passes(satellites, start_time,
                                forward, coords)
    area_boundary = AreaDefBoundary(area, frequency=500)
    area.poly = area_boundary.contour_poly
    for the_pass in sorted(allpasses):
        print("saving", the_pass)
        the_pass.save_fig(poly=area.poly, directory=opts.output_dir)