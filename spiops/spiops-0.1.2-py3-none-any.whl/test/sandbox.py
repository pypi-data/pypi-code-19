from spiops import spiops
import spiops.utils.time as time
from spiops.classes.sensor import Sensor
from spiops.classes.observation import TimeWindow
from spiops.classes.body import Target
from spiops.classes.body import Observer

import spiceypy as cspice


result = spiops.fk_body_ifj2000('JUICE', 'JUPITER',
              '/Users/mcosta/Dropbox/SPICE/SPICE_JUICE/ftp/data/SPICE/JUICE'
              '/kernels/pck/pck00010.tpc',
                 '/Users/mcosta/Dropbox/SPICE/SPICE_JUICE/ftp/data/SPICE/JUICE'
              '/kernels/spk/jup310.bsp', '-28970', report=False, file=False,
              unload=True)

print(result)



#cspice.furnsh('MEX_OPS.TM')
#
#
#interval = TimeWindow('2017-01-25T00:00:00', '2017-01-25T23:00:00', res=60)
#
##try:
##    time_interval = interval.time_set
##
##    print('*******************')
##    for element in time_interval:
##        print(time.et2cal(element))
##
##
##    time_interval = interval.getTimeInterval(format='CAL')
##    print('*******************')
##    for element in time_interval:
##        print(element)
##
##    print(interval.getTime('start'))
##finally:
##    pass
#
#
#mex = Observer('MEX', time=interval)
#mars = Target('MARS', time=interval)
#
#vmc = Sensor('MEX_VMC', host=mex, target=mars, time=interval)
#
#print(vmc.id)
#
#spoint = vmc.getSpoint()
#
#print(spoint)
#
#
#
#
#from mpl_toolkits.mplot3d import Axes3D
#import matplotlib.pyplot as plt
#import numpy as np
#
#xs, ys, zs = [], [], []
#
#
#
#fig = plt.figure()
#ax = fig.add_subplot(111, projection='3d')
#
## For each set of style and range settings, plot n random points in the box
## defined by x in [23, 32], y in [0, 100], z in [zlow, zhigh].
#for element in spoint:
#    xs.append(element[0])
#    ys.append(element[1])
#    zs.append(element[2])
#
#
#ax.scatter(xs, ys, zs)
#
#ax.set_xlabel('X Label')
#ax.set_ylabel('Y Label')
#ax.set_zlabel('Z Label')
#
#
## Make data
#u = np.linspace(0, 2 * np.pi, 360)
#v = np.linspace(0, np.pi, 360)
#x = mars.radii[0] * np.outer(np.cos(u), np.sin(v))            * 0.95
#y = mars.radii[1] * np.outer(np.sin(u), np.sin(v))            * 0.95
#z = mars.radii[2] * np.outer(np.ones(np.size(u)), np.cos(v))  * 0.95
#
## Plot the surface
#ax.plot_surface(x, y, z, color='r')
#
#plt.show()