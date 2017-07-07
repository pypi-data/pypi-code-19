#!/usr/bin/env python
#
# Author: Mike McKerns (mmckerns @caltech and @uqfoundation)
# Copyright (c) 1997-2016 California Institute of Technology.
# Copyright (c) 2016-2017 The Uncertainty Quantification Foundation.
# License: 3-clause BSD.  The full license text is available at:
#  - http://trac.mystic.cacr.caltech.edu/project/pathos/browser/pathos/LICENSE
"""defalut ppserver host and port configuration"""

#tunnelports = ['12345','67890']
tunnelports = []

ppservers = tuple(["localhost:%s" % port for port in tunnelports])

# End of file
