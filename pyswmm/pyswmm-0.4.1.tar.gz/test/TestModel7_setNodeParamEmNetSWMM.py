'''
TestModel1_Current Time

Author: Bryant E. McDonnell (EmNet LLC)
Date: 11/12/2016


'''
import time
import os
import sys
from datetime import datetime, timedelta

#point to location of the pyswmm file
sys.path.append(os.getcwd()+'\\..\\pyswmm\\')

from swmm5 import PySWMM
from toolkitapi import *

swmmobject = PySWMM(r'C:\PROJECTCODE\pyswmm\pyswmm\swmmLinkedLibs\Windows\EmNetSWMM\TestModel1_weirSetting.inp',\
                    r'C:\PROJECTCODE\pyswmm\pyswmm\swmmLinkedLibs\Windows\EmNetSWMM\TestModel1_weirSetting.rpt',\
                    r'C:\PROJECTCODE\pyswmm\pyswmm\swmmLinkedLibs\Windows\EmNetSWMM\TestModel1_weirSetting.out',\
                    r"C:\PROJECTCODE\pyswmm\pyswmm\swmmLinkedLibs\Windows\EmNetSWMM\emnet_swmm5_20170127b.dll")
swmmobject.swmm_open()

print swmmobject.swmm_getNodeParam('J2',NodeParams.invertElev)#, 19 )
swmmobject.swmm_setNodeParam('J2',NodeParams.invertElev, 19 )
print swmmobject.swmm_getNodeParam('J2',NodeParams.invertElev)#, 19 )

print swmmobject.swmm_getLinkParam('C1:C2',LinkParams.offset1)#, 19 )
swmmobject.swmm_setLinkParam('C1:C2',LinkParams.offset1, 19 )
print swmmobject.swmm_getLinkParam('C1:C2',LinkParams.offset1)#, 19 )

print swmmobject.swmm_getSubcatchParam('S2',SubcParams.area)#, 19 )
swmmobject.swmm_setSubcatchParam('S2',SubcParams.area, 19 )
print swmmobject.swmm_getSubcatchParam('S2',SubcParams.area)#, 19 )

swmmobject.swmm_start()

i = 0
while(True):
    
    time = swmmobject.swmm_stride(600)
    i+=1     

    if (time <= 0.0):
        break
    if i %144==0: print i
    swmmobject.swmm_setLinkParam('C1:C2',LinkParams.qLimit, 0.25)
    
swmmobject.swmm_end()
#swmmobject.swmm_report()
swmmobject.swmm_close()

 
print("swmm_step() Check Passed")
