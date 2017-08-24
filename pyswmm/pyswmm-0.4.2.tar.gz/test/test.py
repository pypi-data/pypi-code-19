
import os
import sys

#point to location of the pyswmm file
sys.path.append(os.getcwd()+'\\pyswmm\\')

from ..pyswmm.swmm5 import PySWMM


# this checks the swmmExec process train...

swmmobject = PySWMM('./example/parkinglot.inp',\
                    './example/parkinglot.rpt',\
                    './example/parkinglot.out')

swmmobject.swmmExec()
print(swmmobject.swmm_getVersion())
print(swmmobject.swmm_getMassBalErr())   

print("swmmExec() Check Passed")


#this checks the swmm_step features
swmmobject = PySWMM('./example/parkinglot.inp',\
                    './example/parkinglot.rpt',\
                    './example/parkinglot.out')
swmmobject.swmm_open()
swmmobject.swmm_getSimulationDateTime(0)
swmmobject.swmm_start()

while(True):
    
    time = swmmobject.swmm_step()
##    print time
    if (time <= 0.0):
        break
    
swmmobject.swmm_end()
swmmobject.swmm_report()
swmmobject.swmm_close()

 
print("swmm_step() Check Passed")
