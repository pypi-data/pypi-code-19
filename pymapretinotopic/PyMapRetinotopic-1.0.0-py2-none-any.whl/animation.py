import matplotlib.animation as animation
import numpy as np
from pylab import *


from MonitorSetup import Monitor, Indicator
import StimulusRoutines as stim

mon=Monitor(resolution=(1080, 1920),dis=13.5,
            mon_width_cm=88.8,mon_height_cm=50.1,C2T_cm=33.1,
            C2A_cm=46.4,mon_tilt=16.22,downsample_rate=4)
indicator=Indicator(mon)
KS_stim=stim.KSstim(mon,indicator)

foo, _ = KS_stim.generate_movie()



dpi = 100

def ani_frame():
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    
    temp = foo[0]
    
    im = ax.imshow(rand(300,300))
    im.set_clim([0,1])
    fig.set_size_inches([5,5])


    tight_layout()


    def update_img(n):
        temp = foo[n]
        im.set_data(temp)
        return im

    #legend(loc=0)
    ani = animation.FuncAnimation(fig,update_img,300,interval=30)
    writer = animation.writers['ffmpeg'](fps=30)

    #ani.save('demo.mp4',writer=writer,dpi=dpi)
    return ani