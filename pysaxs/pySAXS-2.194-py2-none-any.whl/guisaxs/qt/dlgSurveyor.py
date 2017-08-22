from PyQt4 import QtGui, QtCore, uic
#from PyQt4.Qt import QString
from fileinput import filename
from pyFAI import azimuthalIntegrator
from pySAXS.guisaxs import dataset
from pySAXS.guisaxs.qt import dlgSurveyorui
from pySAXS.guisaxs.qt import preferences
from pySAXS.guisaxs.qt import QtMatplotlib
from matplotlib import pyplot       # Load matplotlib
from pySAXS.tools import FAIsaxs
from pySAXS.tools import filetools
#from reportlab.graphics.widgets.table import TableWidget
from matplotlib.backends.backend_qt4 import NavigationToolbar2QT as NavigationToolbar
#from spyderlib.widgets.externalshell import namespacebrowser
from time import *
import fabio
import numpy
import os.path, dircache
import pyFAI
import sys
import threading
import glob
import fnmatch

import pySAXS
from  pySAXS.LS import SAXSparametersXML
from pySAXS.guisaxs.qt import dlgQtFAITest

ICON_PATH=pySAXS.__path__[0]+os.sep+'guisaxs'+os.sep+'images'+os.sep  

class SurveyorDialog(QtGui.QDialog):
    def __init__(self, parent=None, parameterfile=None, outputdir=None):
        QtGui.QWidget.__init__(self, parent)
        #self.ui = dlgSurveyorui.Ui_surveyorDialog()
        self.ui = uic.loadUi(pySAXS.UI_PATH+"dlgSurveyor.ui", self)#
        self.setWindowTitle('Continuous Radial averaging tool for pySAXS')
        if parent is not None:
            # print "icon"
            self.setWindowIcon(parent.windowIcon())
        
        #self.ui.setupUi(self)
        QtCore.QObject.connect(self.ui.paramFileButton, QtCore.SIGNAL("clicked()"), self.OnClickparamFileButton)
        QtCore.QObject.connect(self.ui.changeDirButton, QtCore.SIGNAL("clicked()"), self.OnClickchangeDirButton)
        QtCore.QObject.connect(self.ui.STARTButton, QtCore.SIGNAL("clicked()"), self.OnClickSTARTButton)
        QtCore.QObject.connect(self.ui.STOPButton, QtCore.SIGNAL("clicked()"), self.OnClickSTOPButton)
        QtCore.QObject.connect(self.ui.plotChkBox, QtCore.SIGNAL("clicked()"), self.OnClickPlotCheckBox)
        QtCore.QObject.connect(self.ui.btnExtUpdate, QtCore.SIGNAL("clicked()"), self.updateListInit)
        QtCore.QObject.connect(self.ui.tableWidget,QtCore.SIGNAL('cellClicked(int, int)'), self.cellClicked)
        QtCore.QObject.connect(self.ui.btnDisplaySelected, QtCore.SIGNAL("clicked()"), self.btnDisplayClicked)
        QtCore.QObject.connect(self.ui.btnZApply, QtCore.SIGNAL("clicked()"), self.btnZApplyClicked)
        QtCore.QObject.connect(self.ui.btnReset, QtCore.SIGNAL("clicked()"), self.btnZResetClicked)
        QtCore.QObject.connect(self.ui.btnDisplayAV, QtCore.SIGNAL("clicked()"), self.btnDisplayAVClicked)
        QtCore.QObject.connect(self.ui.paramViewButton, QtCore.SIGNAL("clicked()"),self.OnClickparamViewButton)
        self.ui.navi_toolbar = NavigationToolbar(self.ui.matplotlibwidget, self)
        self.ui.verticalLayout_2.insertWidget(0,self.ui.navi_toolbar)#verticalLayout_2
        l=self.ui.navi_toolbar.actions()
        #remove the Pan tool
        l=self.ui.navi_toolbar.actions()
        for i in l:
            #print i.text()
            if i.text()=='Pan':
                panAction=i
            if i.text()=='Customize':
                customizeAction=i
            if i.text()=='Subplots':
                subplotAction=i
            
        #self.ui.navi_toolbar.removeAction(panAction)
        self.ui.navi_toolbar.removeAction(customizeAction)
        self.ui.navi_toolbar.removeAction(subplotAction)
        #--Autoscale
        self.AutoscaleAction= QtGui.QAction('Autoscale', self)
        self.AutoscaleAction.triggered.connect(self.OnAutoscale)
        self.ui.navi_toolbar.addAction(self.AutoscaleAction)
        #-- fix scale
        self.FixScaleAction= QtGui.QAction(QtGui.QIcon(ICON_PATH+'magnet.png'),'Fix Scale', self)
        self.FixScaleAction.setCheckable(True)
        self.FixScaleAction.setChecked(False)
        self.FixScaleAction.triggered.connect(self.OnButtonFixScale)
        self.ui.navi_toolbar.addAction(self.FixScaleAction)
        
        self.SelectedFile=None
        self.ui.labelSelectedFIle.setText("")
        self.ui.btnDisplaySelected.setEnabled(False)
        self.ui.btnDisplayAV.setEnabled(False)
        
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0,1)
        self.ui.STARTButton.setEnabled(True)
        self.ui.STOPButton.setDisabled(True)
        self.parent = parent
        self.plotapp= None
        self.printout = None
        self.whereZ=False
        self.workingdirectory = None
        self.parameterfile=parameterfile
        if self.parameterfile is not None:
            self.ui.paramTxt.setText(str(parameterfile))
            
        self.fai=None
            
         #-- get preferences
        self.pref=preferences.prefs()
        
        if parent is not None:
            self.printout = parent.printTXT
            self.workingdirectory = parent.workingdirectory
            self.pref=self.parent.pref
            print "import pref"
            print self.pref
            print self.pref.getName()
            if self.pref.fileExist():
                self.pref.read()
                print "file exist"
                dr=self.pref.get('defaultdirectory',section="guisaxs qt")
                print "dr :",dr
                if dr is not None:
                    self.workingdirectory=dr
                    #print 'set wd',dr
                    self.ui.DirTxt.setText(self.workingdirectory)
                pf=self.pref.get('parameterfile',section="pyFAI")
                
                if pf is not None:
                    self.parameterfile=pf
                    self.ui.paramTxt.setText(self.parameterfile)
                
                ext=self.pref.get('fileextension',section="pyFAI")
                if ext is not None:
                    self.ui.extensionTxt.setText(ext)
                
            
            else:
                self.pref.save()
            
        else :
            self.workingdirectory = ""
            
        print self.workingdirectory
        self.imageToolWindow = None
        self.updateListInit()
        
    
    
    def OnClickparamFileButton(self):
        '''
        Allow to select a parameter file
        '''
        fd = QtGui.QFileDialog(self)
        filename = fd.getOpenFileName(directory=self.workingdirectory)
        self.workingdirectory = filename
        # print filename
        self.ui.paramTxt.setText(filename)
        # self.ui.editor_window.setText(plik)

    def OnClickSTARTButton(self):
        '''
        Used when start button is clicked
        '''
        print "start"
        self.ui.progressBar.setRange(0,0)
        #print "start2"
        self.radialPrepare()
        #self.ui.progressBar.setValue(100)
        
        self.ui.STOPButton.setEnabled(True)
        self.ui.STARTButton.setDisabled(True)
        if self.ui.refreshTimeTxt.text() == '':
            t = 30
        else :
            t = float(self.ui.refreshTimeTxt.text())    
        #print(time)
        self.t = Intervallometre(t, self.updateList, self)
        self.t.start()
        
    def OnClickSTOPButton(self):
        '''
        Used when stop button is clicked
        '''
        print "stop"
        #self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0,1)
        self.ui.STARTButton.setEnabled(True)
        self.ui.STOPButton.setDisabled(True)
        self.t.stop()
    def OnClickchangeDirButton(self):
        '''
        Allow to select a directory
        '''
        fd = QtGui.QFileDialog(self, directory=self.workingdirectory)
        fd.setFileMode(QtGui.QFileDialog.DirectoryOnly)
        if fd.exec_() == 1:
            #print fd.selectedFiles()
            #dir = str(fd.selectedFiles().first())
            dir = str(fd.selectedFiles()[0])
            # dir=fd.getOpenFileName()
            self.ui.DirTxt.setText(dir)
            self.workingdirectory = dir
            self.updateListInit()
            self.pref.set('defaultdirectory', self.workingdirectory,section="guisaxs qt")
            self.pref.save()
            
    def cellClicked(self,row,col):
        self.SelectedFile=str(self.ui.tableWidget.item(row,0).text())
        self.ui.labelSelectedFIle.setText(self.workingdirectory+os.sep+self.SelectedFile)
        #print self.workingdirectory+os.sep+self.SelectedFile
        self.ui.btnDisplaySelected.setEnabled(True)
        self.ui.btnDisplayAV.setEnabled(True)
        
    def btnDisplayClicked(self):
        if self.SelectedFile is None:
            return
        self.img = fabio.open(self.workingdirectory+os.sep+self.SelectedFile) # Open image file
        
        #pyplot.ion()
        plt=self.ui.matplotlibwidget
        #try:
        #    D=numpy.log(self.img.data)
        #except:
        #    D=self.img.data
        D=self.img.data
        if self.whereZ:
            zmin=float(self.ui.edtZmin.text())
            zmax=float(self.ui.edtZmax.text())
            D=numpy.where(D<=zmin,zmin,D)
            D=numpy.where(D>zmax,zmax,D)
        else:
            self.ui.edtZmin.setText(str(D.min()))
            self.ui.edtZmax.setText(str(D.max()))
        imgplot=plt.axes.imshow(D,cmap="jet")            # Display as an image
        #imgplot.set_cmap('nipy_spectral')
        #--- fix scale
        if self.FixScaleAction.isChecked():
            #axes limits should have been memorized
            plt.axes.set_xlim((self.xlim_min,self.xlim_max))
            plt.axes.set_ylim((self.ylim_min,self.ylim_max))
        plt.draw()
        #pyplot.show()                       # Show GUI window
    
    def btnDisplayAVClicked(self):
        if self.SelectedFile is None:
            return
        self.radialAverage(self.workingdirectory+os.sep+self.SelectedFile)
        
    def OnAutoscale(self):
        print 'autoscale'
        sh=self.img.data.shape
        plt=self.ui.matplotlibwidget
        plt.axes.set_ylim((sh[0],0))
        plt.axes.set_xlim((0,sh[1]))
        self.xlim_min,self.xlim_max=plt.axes.get_xlim()
        self.ylim_min,self.ylim_max=plt.axes.get_ylim()
        plt.draw()
    
    def OnButtonFixScale(self):
        print "OnButtonFixScale"
        #memorize the current scale"
        plt=self.ui.matplotlibwidget
        self.xlim_min,self.xlim_max=plt.axes.get_xlim()
        self.ylim_min,self.ylim_max=plt.axes.get_ylim()
        #print self.xlim_min,self.xlim_max," - ",self.ylim_min,self.ylim_max
            
    def btnZApplyClicked(self):
        try:
            zmin=float(self.ui.edtZmin.text())
            zmax=float(self.ui.edtZmax.text())
            self.whereZ=True
            self.btnDisplayClicked()
            #print zmin, zmax
        except:
            pass
    def btnZResetClicked(self):
        self.whereZ=False
        self.btnDisplayClicked()
    
    def updateList(self):
        '''
        Update the list
        '''
        #print '-UPDATE LIST'
        self.ext = str(self.ui.extensionTxt.text())
        if self.ext == '':
              self.ext = '*.*'
        self.fp = str(self.ui.DirTxt.text())
        #print self.fp
        listoffile = self.getList(self.fp, self.ext)
        #print listoffile
        files=sorted(listoffile,reverse=True)
        #print files
        self.ui.tableWidget.setColumnCount(4)
        self.ui.tableWidget.setRowCount(len(listoffile))
        headerNames = ["File", "date", "processed", "new"]
        self.ui.tableWidget.setHorizontalHeaderLabels(headerNames)
        self.ui.tableWidget.setColumnWidth(0, 220)
        self.ui.tableWidget.setColumnWidth(1, 150)
        self.ui.tableWidget.setColumnWidth(2, 70)
        self.ui.tableWidget.setColumnWidth(3,50)
        i = 0
        for name in files:
            self.ui.tableWidget.setItem(i, 0, QtGui.QTableWidgetItem(name))
            self.ui.tableWidget.setItem(i, 1, QtGui.QTableWidgetItem(str(listoffile[name][0])))
            self.ui.tableWidget.setItem(i, 2, QtGui.QTableWidgetItem(str(listoffile[name][1])))
            self.ui.tableWidget.setItem(i, 3, QtGui.QTableWidgetItem(str(listoffile[name][2])))
            self.ui.tableWidget.setRowHeight(i, 20)
            if not listoffile[name][1] :
                try :
                    self.radialAverage(self.fp + os.sep+ name)
                except:
                    print "unable to average on file :",name
                
            i += 1
        #self.timer()
        self.listoffileVerif = glob.glob(os.path.join(self.fp, self.ext))#filetools.listFiles(self.fp,self.ext)
        self.listoffileVerif = listoffile
        if len(listoffile)>0:
            self.cellClicked(0,0)
            self.btnDisplayClicked()
        else:
            self.SelectedFile=None
            self.ui.labelSelectedFIle.setText("")
            self.ui.btnDisplaySelected.setEnabled(False)
            self.ui.btnDisplayAV.setEnabled(False)
        #print "list updated"

    def updateListInit(self):
        '''
        Update the initial List WITHOUT treatment 
        '''
        #print '-'
        self.ext = str(self.ui.extensionTxt.text())
        if self.ext == '':
              self.ext = '*.*'
        self.fp = str(self.ui.DirTxt.text())
        listoffile = self.getList(self.fp, self.ext)
        files=sorted(listoffile,reverse=True)
        #print listoffile
        
        self.ui.tableWidget.setColumnCount(4)
        self.ui.tableWidget.setRowCount(len(listoffile))
        headerNames = ["File", "date", "processed", "new"]
        self.ui.tableWidget.setHorizontalHeaderLabels(headerNames)
        self.ui.tableWidget.setColumnWidth(0, 220)
        self.ui.tableWidget.setColumnWidth(1, 150)
        self.ui.tableWidget.setColumnWidth(2, 70)
        self.ui.tableWidget.setColumnWidth(3,50)  
        i = 0
        for name in files:
            self.ui.tableWidget.setItem(i, 0, QtGui.QTableWidgetItem(name))
            self.ui.tableWidget.setItem(i, 1, QtGui.QTableWidgetItem(str(listoffile[name][0])))
            self.ui.tableWidget.setItem(i, 2, QtGui.QTableWidgetItem(str(listoffile[name][1])))
            self.ui.tableWidget.setItem(i, 3, QtGui.QTableWidgetItem(str(listoffile[name][2])))
            self.ui.tableWidget.setRowHeight(i, 20)          
            i += 1
        self.listoffileVerif = glob.glob(os.path.join(self.fp, self.ext))#filetools.listFiles(self.fp,self.ext)
        self.listoffileVerif = listoffile
        if len(listoffile)>0:
            self.cellClicked(0,0)
            self.btnDisplayClicked()
        else:
            self.SelectedFile=None
            self.ui.labelSelectedFIle.setText("")
            self.ui.btnDisplaySelected.setEnabled(False)
            self.ui.btnDisplayAV.setEnabled(False)
    
    def getList(self, fp, ext):
        #print "getlist, ",fp,ext
        #print os.path.join(self.fp, self.ext)
        #listoffile = glob.glob(os.path.abspath(self.fp)+os.sep+self.ext)#filetools.listFiles(fp, ext)
        listoffile=[]
        if self.fp=='':
            return []
        for file in os.listdir(self.fp):
            if fnmatch.fnmatch(file, self.ext):
                #print(file)
                listoffile.append(os.path.abspath(self.fp)+os.sep+file)
        
        #print "end glob : ",listoffile
        files = {}
        for name in listoffile:
            fich = filetools.getFilename(name)
            dt = filetools.getModifiedDate(name)
            newfn = filetools.getFilenameOnly(name)
            ficTiff = newfn
            newfn += '.rgr'
            # print newfn
            if filetools.fileExist(newfn) :
                proc = True
                new = False
            else:              
                proc = False
                new = True
            files[fich] = [dt, proc, new]    
        #print "end of getlist: ",files
        return files
    
    
    def printTXT(self, txt="", par=""):
        '''
        for printing messages
        '''
        if self.printout == None:
            print(str(txt) + str(par))
        else:
            self.printout(txt, par)

    def radialPrepare(self):
        self.fai = FAIsaxs.FAIsaxs()
        filename = self.ui.paramTxt.text()
        if not os.path.exists(filename):
            self.printTXT(filename + ' does not exist')
            return
        outputdir = self.ui.DirTxt.text()
        self.fai.setGeometry(filename)
        self.qDiv = self.fai.getProperty('user.qDiv')
        if self.qDiv is None:
            self.qDiv = 1000
        self.mad = self.fai.getIJMask()
        maskfilename = self.fai.getMaskFilename()
  
    def radialAverage(self, imageFilename):
        if self.fai is None :
            self.radialPrepare()
        t0=time()
        im = fabio.open(imageFilename)
        #try:
        SAXSparametersXML.saveImageHeader(im.header,imageFilename)
        self.printTXT("Header file saved")
        #except :
        #        self.printTXT("Error on Header file saving")
        newname = filetools.getFilenameOnly(imageFilename) + ".rgr"
        qtemp, itemp, stemp = self.fai.integrate1d(im.data, self.qDiv, filename=newname, mask=self.mad, error_model="poisson")
        print time()-t0, " s"
        try:
            q = qtemp[numpy.nonzero(itemp)]
            i = itemp[numpy.nonzero(itemp)]
            s = stemp[numpy.nonzero(itemp)]
            self.OnClickPlotCheckBox()
            if self.parent is None:
                self.plotapp.addData(q, i, label=imageFilename)#,error=s)
                self.plotapp.replot()
            else:
                myname=filetools.getFilename(imageFilename)
                self.parent.data_dict[myname]=dataset.dataset(myname,q,i, imageFilename,error=s,type='saxs',image="Image")
                self.parent.redrawTheList()
                if self.ui.plotChkBox.isChecked():
                    self.parent.Replot()        
            
        except:
            print "Error plot"
        self.fai.saveGeometry(imageFilename)#save rpt
        
    def OnClickPlotCheckBox(self):
        if self.parent is None:
            if self.ui.plotChkBox.isChecked():
                self.plotapp=QtMatplotlib.QtMatplotlib()
                self.plotapp.show()
            else:
                self.plotapp.close()
    

    def OnClickparamViewButton(self):
        filename=str(self.ui.paramTxt.text())
        if filename is not None and filename <>'':
            self.dlgFAI=dlgQtFAITest.FAIDialogTest(self.parent,filename,None)
            self.dlgFAI.show()
    
    def closeEvent(self, event):
        '''
        when window is closed
        '''
        #print "close"
        #save the preferences
        if self.parent is not None:
                #self.parent.pref.set("outputdir",section="pyFAI",value=str(self.ui.outputDirTxt.text()))
                self.pref.set("parameterfile",section="pyFAI",value=str(self.ui.paramTxt.text()))
                self.pref.set('defaultdirectory',section="guisaxs qt",value=str(self.ui.DirTxt.text()))
                self.pref.set('fileextension',section="pyFAI",value=str(self.ui.extensionTxt.text()))
                self.pref.save()
        try:
            self.t.stop()
            
        except:
            pass

class Intervallometre(threading.Thread):
 
    def __init__(self, duree, fonction, parent=None):
        threading.Thread.__init__(self)
        self.duree = duree
        self.fonction = fonction
        self.parent = parent
        self.encore = True
        
    def run(self):
        print 'start'
        while self.encore:
            #self.fonction()
            self.parent.updateList()
            self.slip(self.duree)
            '''if self.parent is not None:
                try:
                    val=self.parent.ui.progressBar.value()
                    if val+10>self.parent.ui.progressBar.maximum():
                        self.parent.ui.progressBar.setValue(0)
                    else:
                        self.parent.ui.progressBar.setValue(val+10)
                except:
                    pass'''
    def stop(self):
        self.encore = False
        
    def slip(self,t,intt=1.0):
        if t<intt:
            sleep(t)
            return
        t0=time()
        #print t0,time()-t0
        #self.parent.ui.progressBar.setMaximum(t)
        while t-(time()-t0)>intt:
            print "+",
            #self.parent.ui.progressBar.setValue(t-(time()-t0))
            if self.encore:
                sleep(intt)
                ''''if self.parent is not None:
                    try:
                        val=self.parent.ui.progressBar.value()
                        if val+10>self.parent.ui.progressBar.maximum():
                            self.parent.ui.progressBar.setValue(0)
                        else:
                            self.parent.ui.progressBar.setValue(val+10)
                    except:
                        pass'''
            else:
                return
        sleep(t-(time()-t0))
        
        
        
        
if __name__ == "__main__":
  app = QtGui.QApplication(sys.argv)
  myapp = SurveyorDialog()
  myapp.show()
  sys.exit(app.exec_())
  
