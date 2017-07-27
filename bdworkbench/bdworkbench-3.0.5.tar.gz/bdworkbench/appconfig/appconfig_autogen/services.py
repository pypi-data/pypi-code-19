#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function

def autogenServiceRegistration(outputLines, autogenDict, entryDict):
    """
    Service registration.
    """
    if not autogenDict.has_key('services'):
        return

    outputLines.append("\n")
    for srvcid, srvcDict in autogenDict['services'].iteritems():
        if srvcDict.has_key('sysv'):
            outputLines.append("REGISTER_START_SERVICE_SYSV %s %s\n" % (srvcid,
                                                                        srvcDict['sysv']))

    return
