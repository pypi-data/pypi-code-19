"""Coordinate transformations.

Galactic:
    GC at (0, 0),
    gal. longitude, latitude (l, b)

Horizontal / altaz (km3):
    centered at detector position
    altitude, azimuth (altitude = 90deg - zenith)

EquatorialJ200 / FK5 / ICRS / GCRS
    (right ascension, declination)

    Equatorial is the same as FK5. FK5 is superseded by the ICRS, so use
    this instead. Note that FK5/ICRS are _barycentric_ implementations,
    so if you are looking for *geocentric* equatorial (i.e.
    for solar system bodies), use GCRS.

"""
from astropy.units import rad, deg  # noqa
from astropy.coordinates import (EarthLocation, SkyCoord, AltAz, Longitude,
                                 Latitude, get_sun)
import numpy as np

from km3astro.constants import (
    arca_longitude, arca_latitude, arca_height,
    orca_longitude, orca_latitude, orca_height,
)
from km3astro.time import np_to_astrotime
from km3astro.random import random_date, random_azimuth


ARCA_LOC = EarthLocation.from_geodetic(
    lon=Longitude(arca_longitude * deg),
    lat=Latitude(arca_latitude * deg),
    height=arca_height
)

ORCA_LOC = EarthLocation.from_geodetic(
    lon=Longitude(orca_longitude * deg),
    lat=Latitude(orca_latitude * deg),
    height=orca_height
)


def transform_to_orca(event, time):
    time = np_to_astrotime(time)
    orca_frame = AltAz(obstime=time, location=ORCA_LOC)
    return event.transform_to(orca_frame)


def local_frame(time, loc='orca'):
    if loc == 'orca':
        loc = ORCA_LOC
    if loc == 'arca':
        loc = ARCA_LOC
    frame = AltAz(obstime=time, location=loc)
    return frame


def local_event(azimuth, time, zenith, location='orca'):
    """Create astropy events from detector coordinates."""
    zenith = np.atleast_1d(zenith)
    azimuth = np.atleast_1d(azimuth)

    time = np_to_astrotime(time)
    if location == 'orca':
        loc = ORCA_LOC
    elif location == 'arca':
        loc = ARCA_LOC
    else:
        raise KeyError("Valid locations are 'arca' and 'orca'")
    frame = local_frame(time, loc=loc)

    altitude = zenith - np.pi / 2
    event = SkyCoord(alt=altitude * rad, az=azimuth * rad, frame=frame)
    return event


def sun_in_local(time, loc='orca'):
    time = np_to_astrotime(time)
    local_frame = AltAz(obstime=time, location=ORCA_LOC)
    sun = get_sun(time)
    sun_local = sun.transform_to(local_frame)
    return sun_local


def galcen():
    return SkyCoord(0 * deg, 0 * deg, frame='galactic')


def gc_in_local(time, loc='orca'):
    time = np_to_astrotime(time)
    local_frame = AltAz(obstime=time, location=ORCA_LOC)
    gc = galcen()
    gc_local = gc.transform_to(local_frame)
    return gc_local


def orca_gc_dist(azimuth, time, zenith, frame='detector'):
    """Return angular distance of event to GC.

    Parameters
    ==========
    frame: str, [default: 'detector']
        valid are 'detector', 'galactic', 'icrs', 'gcrs'
    """
    evt = local_event(azimuth, time, zenith)
    galcen = gc_in_local(time, loc='orca')
    if frame == 'detector':
        pass
    elif frame in ('galactic', 'icrs', 'gcrs'):
        evt = evt.transform_to(frame)
        galcen = galcen.transform_to(frame)
    return evt.separation(galcen).radian


def orca_sun_dist(azimuth, time, zenith):
    """Return distance of event to sun, in detector coordinates."""
    evt = local_event(azimuth, time, zenith)
    sun = sun_in_local(time, loc='orca')
    dist = evt.separation(sun).radian
    return dist


def gc_dist_random(zenith, frame='detector'):
    """Generate random (time, azimuth) events and get distance to GC."""
    n_evts = len(zenith)
    time = random_date(n=n_evts)
    azimuth = random_azimuth(n=n_evts)
    dist = orca_gc_dist(azimuth, time, zenith, frame=frame)
    return dist


def sun_dist_random(zenith):
    """Generate random (time, azimuth) events and get distance to GC."""
    n_evts = len(zenith)
    time = random_date(n=n_evts)
    azimuth = random_azimuth(n=n_evts)
    dist = orca_sun_dist(azimuth, time, zenith)
    return dist
