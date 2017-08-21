"""
.. moduleauthor:: Chris Dusold <DriveLink@chrisdusold.com>

A module containing storage classes that maintain small RAM usage and original structure access order.

The motivation for this module was to provide constant size RAM usage
while maintaining normal use of Python Dictionaries and possibly other
structures for semi-big data, where it isn't large enough to warrant more
big data centric solutions.

"""
from drivelink._diskdict import Dict
from drivelink._disklist import List
from drivelink._ordereddiskdict import OrderedDict
