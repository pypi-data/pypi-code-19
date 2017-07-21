# This file is licensed under the CeCILL License
# See LICENSE for details.
"""
author : Olivier Tache
(C) CEA 2015
"""
import sys
from PyQt4 import QtGui, QtCore, uic
from pySAXS.guisaxs.qt import plugin
from pySAXS.guisaxs.qt import dlgAbsoluteI
from pySAXS.guisaxs import dataset
import pySAXS
from pySAXS.mcsas import MCtools
from time import sleep
import numpy
from matplotlib.pyplot import bar
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
from scipy.optimize import curve_fit


classlist=['MCsas'] #need to be specified

def GaussianFunction(x,p0,p1,p2,p3):
        """
        Gaussian model to fit the peak to get exact zero position
        p0 : height of gaussian
        p1 : sigma
        p2 : center of gaussian
        p3 : background
        """
        #print p0,p1,p2,p3
        sigm0=p1#*0.58870501125773733#((2*log(2))**0.5)/2
        return (p0-p3)*numpy.exp(-((x-p2)**2)/(p1*0.58)**2)+p3
    
def prefit(x,y):
        '''
        try to determine some parameters from the datas
        '''
        center=(x[0]+x[-1])/2
        center=x[y.argmax()]
        FWMH=(x[-1]-x[0])/10
        slope=FWMH/2
        maxi=y.max()
        mini=y.min()
        if len(y)>10:
            m=y[:10].mean()
            HalfValue=(maxi-mini)/2
            if HalfValue<m:
                #decreasing front
                t=maxi
                maxi=mini
                mini=t
            #idx = numpy.argmin(numpy.abs(y - HalfValue))
        Arg=[maxi,FWMH,center,mini]
        return Arg

class MCsas(plugin.pySAXSplugin):
    menu="Data Treatment"
    subMenu="MC SAS"
    subMenuText="Start MC"
    icon="mcsas.ico"
    def execute(self):
        datalist=self.ListOfDatasChecked()
        
        #display the dialog box
        label=self.selectedData
        if self.selectedData is None:
            QtGui.QMessageBox.information(self.parent,"pySAXS", "No data are selected", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
            return
        #print self.data_dict[label].parameters
        #print label
        
        self.dlg=dlgMCSAS(self.selectedData,self.parent)
        
    

class dlgMCSAS(QtGui.QDialog):
    def __init__(self, selectedData,parent):
        self.selectedData=selectedData
        self.parent=parent
        datas=self.parent.data_dict[self.selectedData]
        q=numpy.array(datas.q)#*10
        QtGui.QDialog.__init__(self, parent)
        self.popt=None
        self.A=None
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgMCsas.ui", self)
        self.ui.show()
        self.ui.labelDataset.setText(str(selectedData))
        self.ui.editNbSpheres.setText(str(300))
        self.ui.editNbIter.setText(str(5))
        self.ui.editHistBin.setText(str(50))
        self.ui.editLowLim.setText(str(0.1*2*numpy.pi/numpy.max(q)))
        self.ui.editHighLim.setText(str(0.1*2*numpy.pi/numpy.min(q)))
        
        self.ui.editQmin.setText(str(numpy.min(q)))
        self.ui.editQmax.setText(str(numpy.max(q)))
        self.ui.editConvValue.setText(str(1.0))
        self.ui.progressBar.setMaximum(300)
        self.ui.progressBar.setValue(0)
        QtCore.QObject.connect(self.ui.btnFit, QtCore.SIGNAL("clicked()"), self.OnClickFit)
        QtCore.QObject.connect(self.ui.btnCompare, QtCore.SIGNAL("clicked()"), self.OnClickCompare)
        self.hscale='lin'
        self.ui.labelCredits.setText('Small programs for Monte-Carlo fitting of SAXS patterns.\n'+\
                                     'It is released under a Creative Commons CC-BY-SA license. \n'+\
                                     'Please cite as:\n'+\
                                     'Brian R. Pauw, 2012, http://arxiv.org/abs/1210.5304 arXiv:1210.5304.')
        #self.fig2=self.ui.matplotlibwidget.figure
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL("clicked(QAbstractButton*)"), self.click)#connect buttons signal
        self.ui.navi_toolbar = NavigationToolbar(self.ui.matplotlibwidget, self)
        self.ui.verticalLayout_2.insertWidget(0,self.ui.navi_toolbar)
        
        ''''x=numpy.arange(100)
        y=numpy.sin(x)
        self.plt2=self.fig2.add_subplot(111) 
        self.plt2.plot(x,y)
        self.ui.matplotlibwidget.draw()
        '''
    def click(self,obj=None):
        name=obj.text()
        print name
        if name=='Close':
            self.close()
        elif name=='OK':
            
            self.startMC()
            
    def updateUI(self,nr):
        self.ui.progressBar.setValue(nr)
    
    def startMC(self):
        datas=self.parent.data_dict[self.selectedData]
        qmin=float(self.ui.editQmin.text())
        qmax=float(self.ui.editQmax.text())
        print qmin, qmax
        q=numpy.array(datas.q)
        
        nQmin=numpy.where((q>=qmin))[0][0]
        nQmax=numpy.where((q<=qmax))[0][-1]
        q=q[nQmin:nQmax]*10
        #q=numpy.array(datas.q)*10
        I=numpy.array(datas.i)[nQmin:nQmax]
        E=numpy.array(datas.error)[nQmin:nQmax]
        #print E
        q=q[numpy.nonzero(I)]
        itemp=I[numpy.nonzero(I)]
        print numpy.nonzero(I)
        print len(E)
        print len(I)
        E=E[numpy.nonzero(I)]
        I=itemp
        '''self.plt2=self.fig2.add_subplot(111) 
        self.plt2.plot(q,I)
        #self.axes.hold(True)
        
        self.ui.matplotlibwidget.draw()'''


        NbSph=int(self.ui.editNbSpheres.text())
        NbReps=int(self.ui.editNbIter.text())
        H=int(self.ui.editHistBin.text())
        Smin=float(self.ui.editLowLim.text())
        Smax=float(self.ui.editHighLim.text())
        if self.ui.checkBox.isChecked():
            self.hscale='log'
        else:
            self.hscale='lin'
        self.ui.progressBar.setMaximum(NbReps)
        self.ui.progressBar.setValue(0)
        Convcrit=float(self.ui.editConvValue.text())
        self.A=MCtools.Analyze_1D(q,I,numpy.maximum(0.01*I,E),Nsph=NbSph,Convcrit=Convcrit,\
                             Bounds=numpy.array([Smin,Smax]),\
                             Rpfactor=1.5/3,Maxiter=1e4,Histscale=self.hscale,drhosqr=1,Nreps=NbReps,Histbins=H)#feedback=self.updateUI,endf=self.plotBar)
        '''self.c.verbose=False
        self.c.start()'''
        if self.A is None:
            QtGui.QMessageBox.information(self,"pySAXS", "MC SAS could not reach optimization criterion", buttons=QtGui.QMessageBox.Ok, defaultButton=QtGui.QMessageBox.NoButton)
        else:
            self.plotBar()
            self.reDraw()
    

    def reDraw(self):
        self.plt.grid()
        self.fig.tight_layout()
        self.ui.matplotlibwidget.draw()

    def plotBar(self):    
        
        A=self.A
    
        q=A['q']/10
        i=A['Imean']
        #print q
        error=A['Istd']
        name=self.selectedData+ " mc fit"
        self.parent.data_dict[name]=dataset.dataset(name,q,i, name,parent=[self.selectedData],error=error,type='mc_fit')
        self.parent.redrawTheList()
        self.parent.Replot()        
        #plt.bar(A['Hx'][0:-1],A['Hmean']/sum(A['Hmean']),width=A['Hwidth'],yerr=A['Hstd']/sum(A['Hmean']),color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
        #plt.show()
        s=A['Hx'][0:-1] #taille
        V=A['Hmean']/sum(A['Hmean'])
        r=(V*3/4.)**(1./3)    #radius from V
        
        n=r/s  #number
        #print n
        #print sum(n)
        self.fig=self.ui.matplotlibwidget.figure
        #x=numpy.arange(100)
        #y=numpy.sin(x)
        self.fig.clear() 
        self.plt=self.fig.add_subplot(211)
        self.plt.set_title('Particule size distribution')
        w=A['Hwidth']
        self.plt.bar(A['Hx'][0:-1]-w/2,A['Hmean']/sum(A['Hmean']),width=A['Hwidth'],yerr=A['Hstd']/sum(A['Hmean']),color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
        self.plt.set_xlabel("radium (nm)")
        self.plt.set_ylabel('Volume-weighted')
        self.plt.set_ylim(bottom=0.0)
        if self.ui.checkBox.isChecked():
            self.plt.set_xscale('log')
        
        self.plt2=self.fig.add_subplot(212) 
        self.plt2.bar(s-w/2,n,width=A['Hwidth'],color='orange',edgecolor='black',linewidth=1,zorder=2,ecolor='blue',capsize=5)
        self.plt2.set_xlabel("radium (nm)")
        self.plt2.set_ylabel('number')
        if self.ui.checkBox.isChecked():
            self.plt2.set_xscale('log')
        self.plt2.grid()
        #self.reDraw()
        
     
        #self.ui.matplotlibwidget.draw()
    
    
    
    def OnClickFit(self):
        if self.A is None:
            return
        X1=numpy.array(self.A['Hx'][0:-1])
        Y1=numpy.array(self.A['Hmean'])
        #print X1,Y1
        res1=prefit(X1,Y1)    
        print "Prefit result : ",res1
        popt, pcov = curve_fit(GaussianFunction, X1, Y1,p0=res1)
        self.popt=popt
        #plt.plot(X2,Y2, 'b-')
        #plt.grid()
        print "Best Radius :",popt[2], "nm  Sigma : ",popt[1]
        self.plotBar()
        X2=numpy.arange(X1[0],X1[-1],(X1[-1]-X1[0])/200)
        Y2=GaussianFunction(X2, popt[0], popt[1],popt[2],popt[3])
        self.plt.plot(X2,Y2/sum(Y1), 'r-',label='MC SAS r ='+"{:.2f}".format(popt[2])+ "nm  S="+"{:.2f}".format(popt[1]))
        #self.plt.legend(fontsize='x-small')
        self.plt.grid()
        self.reDraw()
        
    def OnClickCompare(self):
        CompM=float(self.ui.editCompMax.text())
        CompR=float(self.ui.editCompR.text())
        CompS=float(self.ui.editCompS.text())
        if self.A is None:
            return
        X1=numpy.array(self.A['Hx'][0:-1])
        Y1=numpy.array(self.A['Hmean'])
        self.plotBar()
        X2=numpy.arange(X1[0],X1[-1],(X1[-1]-X1[0])/200)
        if self.popt is not None:
            Y2=GaussianFunction(X2, self.popt[0], self.popt[1],self.popt[2],self.popt[3])
            self.plt.plot(X2,Y2/sum(Y1), 'r-',label='MC SAS r ='+"{:.2f}".format(self.popt[2])+ "nm  S="+"{:.2f}".format(self.popt[1]))
        Y3=GaussianFunction(X2,CompM, CompS, CompR,0.0)
        self.plt.plot(X2,Y3, 'g-',label='pySAXS r ='+"{:.2f}".format(CompR)+ "nm  S="+"{:.2f}".format(CompS))
        self.plt.grid()
        self.plt.legend(fontsize='x-small')
        self.reDraw()