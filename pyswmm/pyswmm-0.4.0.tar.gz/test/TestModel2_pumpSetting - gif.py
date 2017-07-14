'''
PySWMM Test 2: Pump Setting and Simulation Results Streaming

Author: Bryant E. McDonnell (EmNet LLC)
Date: 11/15/2016

'''

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib._png import read_png
from matplotlib.offsetbox import OffsetImage, AnnotationBbox


import os
import sys

#point to location of the pyswmm file
sys.path.append(os.getcwd()+'\\..\\pyswmm\\')

from pyswmm import Simulation, Nodes, Links


with Simulation('./TestModel2_pumpSetting.inp') as sim:
    sim._model.swmm_start()
    LinkC3 = Links(sim)['C3']
    NodeJ1 = Nodes(sim)['J1']


    fig = plt.figure()
    ax = fig.add_subplot(2,3,(1,2))
    ax.set_ylabel('Flow Rate')
    line, = ax.plot([], [], label = 'C3')
    ax.grid()
    ax.legend()

    ax2 = fig.add_subplot(2,3,(4,5), sharex=ax)
    ax2.set_ylabel('Setting')
    line2, = ax2.plot([], [], label = 'C2')
    ax2.grid()

    xdata, ydata = [], []
    ydata2 = []

    ax3 = fig.add_subplot(2,3,(3,6))

    arr_lena = read_png("./TestModel1_weirSetting.PNG")
    imagebox = OffsetImage(arr_lena, zoom=0.67)
    ab = AnnotationBbox(imagebox, (0.5,0.5),
                        xybox=(0.5,0.5),
                        xycoords='data',
                        boxcoords="offset points",
                        pad=0.0,
                        )
    ax3.add_artist(ab)
    ax3.axis('off')

    def data_gen(t=0):
        i = 0
        while(True):

            time = sim._model.swmm_stride(1500)
            i+=1
            if i == 25-10:
                LinkC3.target_setting = 0.9
            if i == 30-10:
                LinkC3.target_setting = 0.8
            if i == 35-10:
                LinkC3.target_setting = 0.7
            if i == 40-10:
                LinkC3.target_setting = 0.6
            if i == 45-10:
                LinkC3.target_setting = 2.0
            if i == 50-10:
                LinkC3.target_setting = 0.4
            if i == 55-10:
                LinkC3.target_setting = 0.3
            if i == 60-10:
                LinkC3.target_setting = 0.2
            if i == 75-10:
                LinkC3.target_setting = 0.1
            if i == 80-10:
                LinkC3.target_setting = 0.0          
            if i == 90-10:
                LinkC3.target_setting = 1.0
                
            if i > 0 and time == 0.0:
                break
            if i > 0 and time > 0:
                yield time        
    def run(t):
        
        xdata.append(t)
        new_y = LinkC3.flow
        ydata.append(new_y)
        
        new_y2 = LinkC3.target_setting
        ydata2.append(new_y2)
        
        xmin, xmax = ax.get_xlim()
        ymin, ymax = ax.get_ylim()
        ymin2, ymax2 = ax2.get_ylim()

        #ax
        if new_y > ymax:
            ax.set_ylim(-0.1, 1.5*ymax)
        if t >= xmax:
            ax.set_xlim(xmin, 1.5*xmax)
            ax.figure.canvas.draw()
        line.set_data(xdata, ydata)

        #ax1
        if new_y2 > ymax2:
            ax2.set_ylim(-0.1, 1.2*ymax2)
        line2.set_data(xdata, ydata2)    


    ani = animation.FuncAnimation(fig, run, data_gen, blit=False,repeat=False, save_count=300, interval = 5)

    ShowFig = False
    if ShowFig == True:
        plt.show()
    else:
        ani.save('SetPumpSetting.gif', dpi=200, writer='imagemagick')
        
    #if 0 == 0:  
    #    from JSAnimation import HTMLWriter
    #    ani.save('LivePlotTest.html', writer=HTMLWriter(embed_frames=False),extra_args=['figsize',[15,6],'dpi',170])

    plt.close()

    sim._model.swmm_end()
    sim._model.swmm_report()
    sim._model.swmm_close()

 
print("Check Passed")
