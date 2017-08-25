import multiprocessing
import os
import threading
import time
from .Config import configer
from .DatetimePlus import DatetimePlus


class Logger(object):
    __logList = None
    __isPrint = True
    __level = 0
    __levelDict = {
        1:'Debug',
        2:'Info',
        3:'Warning',
        4:'Error',
        5:'Fatal'
    }
    __logPath = ''

    def createFileName(self,level):
        dateStr = DatetimePlus.getNowDateToStr()
        result = dateStr + '_' + self.__levelDict.get(level,'Normal') + '.log'
        return result


    def write(self,s,level,dt):
        s = dt + ':' + str(s)
        if self.__isPrint:
            print(s)
        if level < self.__level:
            return
        fileName = self.__logPath + self.createFileName(level)
        with open(fileName,'a') as f:
            f.write(s + '\r\n')

    def info(self,s):
        self.__logList.put([s,2,DatetimePlus.getNowToStr()])

    def debug(self,s):
        self.__logList.put([s, 1,DatetimePlus.getNowToStr()])

    def warning(self,s):
        self.__logList.put([s, 3,DatetimePlus.getNowToStr()])

    def error(self,s):
        self.__logList.put([s,4,DatetimePlus.getNowToStr()])

    def fatal(self,s):
        self.__logList.put([s, 5,DatetimePlus.getNowToStr()])

    def normal(self,s):
        self.__logList.put([s, 0,DatetimePlus.getNowToStr()])

    def __getQueue(self):
        while True:
            try:
                lv = self.__logList.get(timeout=1)
                self.write(lv[0],lv[1],lv[2])
            except Exception as e:
                pass


    def __init__(self):
        self.__day = int(configer.Root['options']['Logger']['SaveDay'])
        self.__level = int(configer.Root['options']['Logger']['Level'])
        self.__isPrint = str(configer.Root['options']['Logger']['IsPrint']).lower() == 'true'
        self.__logList = multiprocessing.Queue()
        self.__logPath = configer.Root['options']['filePath'] + 'Logs/'
        if not os.path.exists(self.__logPath):
            os.makedirs(self.__logPath)
        self.thread = threading.Thread(target=self.__getQueue,args=())
        self.thread.daemon = True
        self.thread.start()

logger = Logger()