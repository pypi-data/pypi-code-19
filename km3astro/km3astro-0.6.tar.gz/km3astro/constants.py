"""Constants, like geographical positions."""

import utm

HEMISPHERE = 'north'
DATUM = 'WGS84'

# TODO: get true UTM coordinates!
orca_latitude = 42 + (48 / 60)  # degree
orca_longitude = 6 + (2 / 60)  # degree
orca_height = -2450  # m

orca_easting, orca_northing, orca_utm_zone_number, orca_utm_zone_letter = \
    utm.from_latlon(orca_latitude, orca_longitude)
orca_utm_zone = '{num}{let}'.format(
    num=orca_utm_zone_number, let=orca_utm_zone_letter)

# taken from detX v2
arca_northing = 4016800
arca_easting = 587600
arca_height = -3450  # m
arca_utm_zone_number = 33
arca_utm_zone_letter = 'N'
arca_utm_zone = '{num}{let}'.format(num=arca_utm_zone_number, let=arca_utm_zone_letter)
arca_latitude, arca_longitude = utm.to_latlon(arca_easting, arca_northing,
                                              arca_utm_zone_number,
                                              arca_utm_zone_letter)
