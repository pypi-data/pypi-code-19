# Standard library imports
from datetime import timedelta

# Local imports
#from pyswmm import Simulation
#from pyswmm.tests.data import MODEL_WEIR_SETTING_PATH

###def test_current_time():
##with Simulation(r"C:\KCMOModeling\Model\KCMOMergedModel - Base.inp") as sim:
##
####    start = sim.start_time
####    print(start)
####    endtime = sim.end_time
####    print(endtime)
####    
####    print(start + timedelta(hours = 30))
####    sim.start_time = start + timedelta(hours = 30)
####    sim.end_time = endtime + timedelta(hours = 30)
####    print("\n\n\nDates\n")
##    for step in sim:
##        start = sim.start_time
##        print(start)        
##        #assert (sim.current_time >= sim.start_time)
##        #assert (sim.current_time <= sim.end_time)

from pyswmm import swmm5
sim = swmm5.PySWMM("C:\\PROJECTCODE\\pyswmm\\pyswmm\\tests\\data\\model_pump_setting.inp")
sim.swmm_open()

#sim.SWMMlibobj.swmm_getAPIError()

sim.swmm_close()
