#
# Copyright (c) 2016 BlueData Software, Inc.
#

from __future__ import print_function



def autogenExecute(outputLines, autogenDict, entryDict):
    """
    Handle any pattern replacements requested by the user.
    """
    if not autogenDict.has_key('execute'):
        return

    
    for script in autogenDict['execute']:
        print(script)
        #print("DEBUG:",containerDst,replaceDict)
        #replaceDict = autogenDict['replace'][containerDst]
        scriptPath = "${CONFIG_BASE_DIR}/" + script
        outputLines.append("chmod 777 %s\n" %(scriptPath))
        outputLines.append("sh %s && (echo %s successful || exit 1)\n" %(scriptPath,scriptPath))
        outputLines.append("\n")
    return
