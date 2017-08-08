# -*- coding: utf-8 -*-

r""" PyCAPO: CAPO Integration for Python

CAPO stands for CASA, Archive and Pipeline Options, and it is a system that caches and fetches configuration settings from a hierarchy of property files. This was initially developed to handle the NRAO's data reduction pipeline and archive retrieval system, the first implementation was in Java and was a simple wrapper over Apache Commons.Configuration: behold, a Python version.

CAPO understands two main concepts, a 'path' of directories to search and a 'profile' name, e.g. 'test', 'production', 'staging' and so on. The path is a colon delimited list of directories to be searched in the order first to last, with properties on later files over-writing those from earlier files. In each directory listed on the path CAPO looks for $profile.properties, e.g. test.properties, production.properties.

:General Notes:

Property files are assumed to be in the standard format Java uses, text files of lines of key=value pairs. The keys are case-insensitive and have no whitespace in them. Blank lines are skipped and lines that start with a ';' or a '#' are considered comments and ignored. Unlike Python property files, Java property files don't include [] sections, adding a section like that would probably break pycapo. Note that Java property files can do expansion of environment variables, PyCAPO can as well but support for it is rudimentary.

At this time the Java CAPO ships with two APIs, an older, lower level one ('CAPO Classic') and a newer type-safe one ('CAPO New Formula'). PyCAPO currently only speaks CAPO Classic. Also, the default path is very NRAO-specific and you will likely need to call this with a specific path or set your CAPO_PATH environment variable to one that suits you.

See the CAPO docs (https://open-confluence.nrao.edu/display/SSA/Capo) for more information.
"""

from pycapo._constants import DEFAULT_CAPO_PATH
from pycapo.models import CapoConfig, Settings
from pycapo._version import ___version___ as version
