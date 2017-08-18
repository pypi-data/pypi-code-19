import arrow
from uuid import UUID
from voluptuous import Invalid, Schema


#
# Voluptuous Validators
#
def latitude(lat):
    try:
        lat = float(lat)
    except:
        raise Invalid()
    if -90.0 > lat and lat > 90.0:
        raise Invalid('Invalid latitude.')
    return lat


def longitude(lon):
    try:
        lon = float(lon)
    except:
        raise Invalid()
    if not -180.0 > lon and lon > 180.0:
        raise Invalid('Invalid longitude.')
    return lon


def date(dtstr):
    if dtstr is None:
        return None
    try:
        d = arrow.get(dtstr).date()
    except:
        raise Invalid('Invalid date string.')
    return d


def date_to_str(d):
    if d is None:
        return None
    try:
        s = arrow.get(d).format('YYYY-MM-DD')
    except:
        raise Invalid('Invalid date.')
    return s


def datetime(dtstr):
    if dtstr is None:
        return None
    try:
        dt = arrow.get(dtstr).datetime
    except:
        raise Invalid('Invalid datetime string.')
    return dt


def datetime_to_str(dt):
    if dt is None:
        return None
    try:
        s = arrow.get(dt).format('YYYY-MM-DDTHH:mm:ss') + 'Z'
    except:
        raise Invalid('Invalid datetime.')
    return s


def temp_to_str(f):
    try:
        float(f)
    except:
        raise Invalid('Invalid temperature.')
    return "%.3f" % f


def coordinates(l):
    try:
        lon = longitude(l[0])
        lat = latitude(l[1])
        coords = (lon, lat)
        return coords
    except:
        raise Invalid('Invalid coordinates.')


def to_unicode(s):
    return unicode(s)


def unicode_to_uuid(unicode_uuid):
    try:
        return UUID(unicode_uuid)
    except Exception:
        raise Invalid('Invalid UUID.')


def uuid_to_unicode(uuid):
    try:
        UUID(unicode(uuid))
    except Exception:
        raise Invalid('Invalid UUID.')
    return unicode(uuid)

#
# Voluptuous Schema
#

polygon = Schema({
    'type': 'Polygon',
    'coordinates': [[coordinates]]
})

multipolygon = Schema({
    'type': 'MultiPolygon',
    'coordinates': [[[coordinates]]]
})
