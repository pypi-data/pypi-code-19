from os import listdir
from os.path import join as pjoin
from os.path import basename, isfile, abspath
from .qtWidgets import ListWidgetItem



__all__ = ["lutListWidgetItem","LUTs"]

class lutListWidgetItem(ListWidgetItem):
    def __init__(self,name,path):
        super(lutListWidgetItem, self).__init__(name,path)
class LUTs(object):

    def __init__(self,folder=None,arrayOfLutFiles=None):

        if folder != None:
            self.folder = folder
        elif arrayOfLutFiles != None:
            if type(arrayOfLutFiles) == list:
                self.luts = []
                for lut in arrayOfLutFiles:
                    if isfile(abspath(lut)):
                        self.luts.append(abspath(lut))
            self.luts = arrayOfLutFiles



    @property
    def folder(self):
        return self._folder

    @folder.setter
    def folder(self,folderpath):
        self.luts = []
        self._folder = folderpath
        if folderpath != 0:
            for lut in listdir(folderpath):
                if lut.endswith(".cube"):
                    self.luts.append(pjoin(self.folder, lut))


    def qtListItems(self):
        for lut in self.luts:
            yield lutListWidgetItem(basename(lut)[:-5],lut)
