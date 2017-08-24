#import matplotlib.pyplot as plot

import numpy as np


import time

import os
import sys

#point to location of the pyswmm file
sys.path.append(os.getcwd()+'\\..\\pyswmm\\')

from swmm5 import PySWMM
from toolkitapi import *





swmmobject = PySWMM('./TestModel1_weirSetting.inp',\
                    './TestModel1_weirSetting.rpt',\
                    './TestModel1_weirSetting.out')
swmmobject.swmm_open()

swmmobject.swmm_start()



i = 0
while(True):
    
    time = swmmobject.swmm_stride(600)
    i+=1
    print swmmobject.swmm_getCurrentSimualationTime()
    #print type(swmmobject.swmm_getCurrentSimualationTime())
    fin = swmmobject.swmm_getCurrentSimualationTime()
    if i == 80:
        swmmobject.swmm_setLinkSetting('C3',0.9)
    if i == 90:
        swmmobject.swmm_setLinkSetting('C3',0.8)
    if i == 100:
        swmmobject.swmm_setLinkSetting('C3',0.7)
    if i == 110:
        swmmobject.swmm_setLinkSetting('C3',0.6)
    if i == 120:
        swmmobject.swmm_setLinkSetting('C3',0.5)
    if i == 130:
        swmmobject.swmm_setLinkSetting('C3',0.4)
    if i == 140:
        swmmobject.swmm_setLinkSetting('C3',0.3)
    if i == 150:
        swmmobject.swmm_setLinkSetting('C3',0.2)
    if i == 160:
        swmmobject.swmm_setLinkSetting('C3',0.1)
    if i == 170:
        swmmobject.swmm_setLinkSetting('C3',0.0)          
    if i == 220:
        swmmobject.swmm_setLinkSetting('C3',1.0)        

    if (time <= 0.0):
        break
    if i %144==0: print i
    
swmmobject.swmm_end()
swmmobject.swmm_report()
swmmobject.swmm_close()

 
print("swmm_step() Check Passed")
