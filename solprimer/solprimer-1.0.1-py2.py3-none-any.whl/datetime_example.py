"""
datetime_example.py
=====
test the main time-related functions from the 'datetime' package

developed with Python3.5, tested with Python2.7
*** does not work under Python 2.7, because the datetime
object has no attribute 'timezone' ***


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

import datetime as dt


# build a datetime object with year, month, day, hour, minute, timezone
#

# get system values for local time, alternatively the values can be
# assigned manually (all integers)
year = dt.datetime.today().year
month = dt.datetime.today().month
day = dt.datetime.today().day
hour = dt.datetime.today().hour
minute = dt.datetime.today().minute

# the timezone tz needs to be inserted manually
# tz can have a fractional part, this is required by some timezones
# positive tz values East, negative tz values West of Greenwich
tz = -2.5     # timezone in hours 

print (year, month, day, hour, minute, tz)


# timezone can only be assigned via timedelta, see Python doc 8.1.7
# (timezone objects)
# summer delayed time is not dealt with explicitly in the timezone class,
# it needs to be combined in the tz parameter before this is passed to
# the constructor

tz = dt.timezone(dt.timedelta(minutes=tz*60)) 


# date and time constructor
localdate = dt.datetime(year, month, day, hour, minute, tzinfo=tz)


print ('localdate', localdate)

print ('localdate.time()', localdate.time())

print ('localdate.timetz()', localdate.timetz())

print ('localdate.astimezone()', localdate.astimezone())    

print ('localdate.utcoffset()', localdate.utcoffset())

print ('localdate.dst()', localdate.dst())

print ('localdate.tzname()', localdate.tzname())

print ('localdate.tzinfo', localdate.tzinfo)

print ()

print ('localdate.timetuple', localdate.timetuple())

print ()

print ('localdate.utctimetuple', localdate.utctimetuple())

print ()

print ('localdate.timetuple().tm_yday', localdate.timetuple().tm_yday)

print ()

print ('localdate.timetuple().tm_gmtoff', localdate.timetuple().tm_gmtoff)

print ()


