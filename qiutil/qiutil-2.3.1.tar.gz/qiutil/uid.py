import time
import calendar
import struct
import base64

MODULO_FACTOR = dict(
    u=1000000,
    m=1000,
    s=1,
    h=1.0/60,
    d=1.0/(60*24)
)
"""
The :meth:`generate_uid` modulo unit factors.
"""

def generate_uid(**opts):
    """
    Makes an id that is unique modulo a given duration unit. The id
    is unique to within one duration unit of calling this function
    for the execution context which runs this method. The default
    modulo unit is microseconds (``u``). Other supported durations
    are milliseconds (``m``), seconds (``s``), hours (``h``) and
    days (``d``).

    This is a simple, fast id generator that is adequate for most
    purposes.

    The base year parameter should be no greater than the current
    year and should not change over the lifetime of all objects
    created using that year. A higher base year results in a smaller
    UID.

    :param opts: the following options:
    :option modulo: the optional modulo unit parameter
    :option year: the optional base year for the time offset
      (default 2001)
    :param modulo: the modulo unit (default 'u')
    :rtype: long
    :return: the UID
    """
    # The default year is 2001.
    year = opts.get('year', 2001)
    # The default modulo unit is 'u'.
    modulo = opts.get('modulo', 'u')
    # A starting time prior to now.
    start = time.mktime(calendar.datetime.date(year, 01, 01).timetuple())
    # The scaling factor.
    factor = MODULO_FACTOR.get(modulo, None)
    if not factor:
        raise ValueError("The module factor is not supported: %s" % modulo)
    # A long which is unique to within one microsecond.
    return long((time.time() - start) * factor)


def generate_string_uid(**opts):
    """
    Makes a string id based on the :meth:`generate_uid` value.
    The string id is a URL-safe base64-encoded string without trailing
    filler or linebreak. It is thus suitable for file names as well as
    URLs.

    The generated id is ten characters long for the default base year.

    :param opts: the :meth:`generate_uid` options
    :rtype: str
    :return: the string UID
    """
    # The long uid.
    uid = generate_uid(**opts)
    # Encode the long uid without trailing filler or linebreak.
    return base64.urlsafe_b64encode(struct.pack('L', uid)).rstrip('A=\n')
