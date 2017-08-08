from astropy.units import hourangle, deg
from astropy.coordinates import SkyCoord


SIRIUS = SkyCoord('06 45 08.9 -16 42 58', unit=(hourangle, deg))
CANOPUS = SkyCoord('06 23 57.1 -52 41 45', unit=(hourangle, deg))
ARCTURUS = SkyCoord('14 15 39.7 +19 10 57', unit=(hourangle, deg))
ANTARES = SkyCoord('16 29 24.4 -26 25 55', unit=(hourangle, deg))
