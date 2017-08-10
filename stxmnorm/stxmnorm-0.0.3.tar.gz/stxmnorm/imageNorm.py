#!/usr/bin/python
""" this class deal with image normalizing process
v01 updates:
        - don't return the figure anymore
        - 
        
"""
__author__="carlos"
__date__ ="$ Fev/2017 $"


import numpy as np

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import matplotlib.patches as patches
from matplotlib.transforms import Bbox
from matplotlib.widgets import  RectangleSelector

from scipy.misc import imread

##from scipy import ndimage

import sys


class imageNorm(object):

        def __init__(self):
                # Global variables
                self.img_orig = None
                self.img = None
                self.imgplot = None
                self.caxes = None
                self.axes = None
                self.mouseispressed = None
                self.openfileformat = None
                self.pathssvfile = None
                
                self.fig = plt.figure()
                self.axes = self.fig.add_subplot(111)
                
                # Creates a patch to use as selection area and add it to the main axes
##                self.selection = patches.Rectangle((0,0), 0, 0)
                self.x0 = None
                self.y0 = None
                self.x1 = None
                self.y1 = None
                self.list_rectangles = []
                

        def loadImage(self, fname):
                if fname[-3:len(fname)] == "ssv":
                        self.openfileformat = "ssv"
                        self.img = np.genfromtxt(fname, dtype=np.int32)
                        self.img_orig = np.genfromtxt(fname, dtype=np.int32)                                               
                else:
                        self.img = imread(fname)
                        if len(self.img.shape) > 2:
                                "3d image"
                                self.img = self.img[:,:,0]
                        df = np.random.uniform(low=0.9, high=1.1, size=self.img.shape[1])
                        self.img = (self.img*df).astype(np.float32)
##                        self.img = np.rot90(self.img)
                        print "shape opened image: ", self.img.shape
            

##                if self.selection != None:
##                        self.axes.add_patch(self.selection)                

                """ Rotine to create self.imgplot """
                self.imgplot = plt.imshow(self.img, cmap='gray', interpolation='none')
##                self.imgplot.set_axes(self.axes)
##                self.fig.add_axes(self.axes)                
##                self.axesAdjustment()                
                
                return self.imgplot.figure


        def saveProject(self, fname, savename):
                index = savename.rindex("/")
                path = savename[0:index+1]
                name = savename[index+1:len(savename)]                
                prefix = "imageNorm_"
                
                with h5.File(path + prefix + name + ".h5", "w") as hf:
##                        data = self.roll.transfRoll(self.img, self.transformation, 0)                      
##                        hf.create_dataset("stxm", data=self.roll.transfRoll(self.img, (-1)*self.transformation, 0), dtype=np.int32)
##                        hf.create_dataset("test", data=self.img, dtype=np.int32)
                        hf.create_dataset("stxm", data=self.img_orig, dtype=np.int32)
                        if self.openfileformat == "ssv":
                                hf["stxm"].attrs["filepath"] = fname
                        else:
                                hf["stxm"].attrs["filepath"] = self.pathssvfile
                        hf.create_dataset("transformation", data=self.transformation, dtype=np.int16)
                        hf.close()
                        
                
        def exportImage(self, savename):                
                mpimg.imsave(savename + '.tiff', self.img, cmap='gray', format=None)                
                        

        def resetImage(self, fname):
##                self.imgplot.axes.clear()
                self.clearSelection(True)
                self.loadImage(fname)
                

        def removeFigure(self):
                self.clearSelection(True)
                

        def axesAdjustment(self):
                print "called"
                # Extent 
                extent = self.imgplot.get_extent()
                print extent # extent is a tuple (left, right, bottom, top)
                self.imgplot.set_extent((0.0, self.img.shape[1], self.img.shape[0], 0.0 ))

                # xlim and ylim
##                self.imgplot.axes.set_xlim(0, 250)
##                self.imgplot.axes.set_ylim(260, 0)

                # Scale
                self.imgplot.autoscale()                
                self.imgplot.axes.relim()
##                self.imgplot.axes.autoscale()
##                self.imgplot.axes.autoscale_view(tight=True, scalex=False, scaley=False)
                
                self.axes = self.imgplot.axes


        def onSelect(self, eclick, erelease):
                print eclick.button        
                self.x0 = eclick.xdata
                self.y0 = eclick.ydata
                print "start position: ", self.x0, self.y0
                self.x1 = erelease.xdata
                self.y1 = erelease.ydata
                print "end position: ", self.x1, self.y1
                

        def onPress(self, event):
                print "pressed"
##                self.mouseispressed = True
##                if self.axes == self.caxes:
##                        self.x0 = event.xdata
##                        self.y0 = event.ydata                        
                                            
                       
        def onRelease(self, event):
                print "released"
                self.y0 = int(round(self.y0, 0))
                self.y1 = int(round(self.y1, 0))
                self.x0 = int(round(self.x0, 0))
                self.x1 = int(round(self.x1, 0))
                if self.y0 > self.y1:
                        aux = self.y0
                        self.y0 = self.y1
                        self.y1 = aux
                if self.x0 > self.x1:
                        aux = self.x0
                        self.x0 = self.x1
                        self.x1 = aux
                print self.x0, self.x1, self.y0, self.y1
                
                if self.axes == self.caxes:
                        self.selection = patches.Rectangle((self.x0, self.y0), self.x1 - self.x0, self.y1 - self.y0,
                                                           alpha=0.5, facecolor='red', edgecolor='black', linewidth=2)
##                        print self.selection.get_xy(), self.axes.patches[len(self.axes.patches)-1].get_xy()
                        if self.selection.get_xy() != self.axes.patches[len(self.axes.patches)-1].get_xy():
                                self.axes.add_patch(self.selection)
                                self.list_rectangles.append([self.x0, self.x1, self.y0, self.y1])
                                print "list of rectangles", self.list_rectangles, "\n", len(self.list_rectangles)
                                print self.list_rectangles[0][0]
                print "len of patches list:", len (self.axes.patches)
##                print "patches:", self.axes.patches
##                for patch in self.axes.patches:
##                        print "vertices", patch.get_path(), "xy:", patch.get_xy(),\
##                              "widht:", patch.get_width(), "height:", patch.get_height()
                return self.y0, self.y1
        

        def onMotion(self, event):
                self.caxes = event.inaxes
##                if self.axes == self.caxes and self.mouseispressed:
##                    self.x1 = event.xdata
##                    self.y1 = event.ydata
##                    self.selection.set_width(self.x1 - self.x0)
##                    self.selection.set_height(self.y1 - self.y0)
##                    self.selection.set_xy((self.x0, self.y0))
##                    self.selection.set_facecolor("none")
##                    self.selection.set_edgecolor("black")
##                    self.axes.figure.canvas.draw()
##                    self.selection.set_width(0)                    
##                    self.selection.set_xy((self.x0, self.y0))
##                    self.selection.set_facecolor("none")
##                    self.selection.set_edgecolor("b")
##                    self.axes.figure.canvas.draw()
                

        def normImage(self):
                """Single line based"""
##                whitespaceline = 80
##                nf = self.img[whitespaceline, :].mean() / self.img[whitespaceline, :]
##                self.img = self.img * nf
                
                """Multiple selections"""
                if len(self.axes.patches) < 3: # If there is only on selection drawed
                        print "\none selection\n"
                        x0, x1, y0, y1 = self.x0, self.x1, self.y0, self.y1
                        nf_00 = self.img[y0:y1, :].mean(0).mean() / self.img[y0:y1, :].mean(0)
                        nf_01 = self.img[y0:y1, x0:x1].mean(0).mean() / self.img[y0:y1, :].mean(0)

                        nf_10 = self.img[y0:y1, :].mean(1).mean() / self.img[y0:y1, :].mean(0)
                        nf_11 = self.img[y0:y1, x0:x1].mean(1).mean() / self.img[y0:y1, :].mean(0)

                        print "nf00:", self.img[y0:y1, :].mean(0).mean(), " nf01:", self.img[y0:y1, x0:x1].mean(0).mean()
                        print "nf10:", self.img[y0:y1, :].mean(1).mean(), " nf11:", self.img[y0:y1, x0:x1].mean(1).mean()

                        print "nf_00", nf_00.mean(), "nf_01", nf_01.mean()
                        print "nf_10", nf_10.mean(), "nf_11", nf_11.mean()
                        
                        print "width:", x1-x0, "lenght:", y1-y0
                        nf = nf_00
##                        self.img = self.img * nf_00
##                        self.img = self.img * nf_10
##                        self.imgplot.set_data(self.img)
                        print "shape of nf:", nf.shape
                else: # If there are more than one selection drawed
                        print "\nmultiple selection\n"
                        nfs = np.zeros((len(self.list_rectangles), self.img.shape[1]))
                        i = 0
                        for rec in self.list_rectangles:
                                x0, x1, y0, y1 = rec[0], rec[1], rec[2], rec[3]
                                print x0, x1, y0, y1
                                nf = self.img[y0:y1, :].mean(0).mean() / self.img[y0:y1, :].mean(0)
                                nfs[i,:] = nf
                                i += 1
                        print nfs.mean(0).shape
                        nf = nfs.mean(0)
                        
                self.img = self.img * nf
                self.imgplot.set_data(self.img)
                

        def clearSelection(self, radio):
                
                if len(self.axes.patches) > 1:
                        self.axes.patches[len(self.axes.patches)-1].remove()
                        del self.list_rectangles[-1]
                        print radio, "list_rectangles", len(self.list_rectangles), "axes_patches",len(self.axes.patches)
                if radio:
                        [patch.remove() for patch in self.axes.patches[1:len(self.axes.patches)]]
                        self.list_rectangles = []
                        print radio, "list_rectangles", len(self.list_rectangles), "axes_patches",len(self.axes.patches)
                                
              

                























                
                
                
     
