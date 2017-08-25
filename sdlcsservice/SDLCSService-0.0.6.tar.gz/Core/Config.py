
def Singleton(cls):
    __instance = {}
    def getInstance(*args,**kwargs):
        if cls not in __instance:
            __instance[cls] = cls(*args,**kwargs)
        return __instance[cls]
    return getInstance

@Singleton
class Configer(object):
    __FileSize = 1048576  #单位 字节
    __FilePath = '/data/'
    __Host = '0.0.0.0'
    __Port = 8080
    __IsDebug = True
    __ThreadCount = 1
    __interfaceModules = []
    __serviceModules = []
    __ServicesInfo={}
    __IsPrintError = True
    __UnLimitedIP =[]
    __HostInfo = {}
    __AsyncTheadCount = 1
    __AsyncTimeOut = 60
    __setDict = None
    __Database = None

    def __init__(self,*args,**kwargs):
        self.__fileName = args[0]
        import os
        if not os.path.exists(self.__fileName):
            with open('Config.json','w') as f:
                f.write('''{
"ServiceModules":{
"SDLCSUnit":{
"loopTime":"5"
}
},
"options":{
"fileSize":"2048",
"filePath":"/data/",
"port":"80",
"debug":"True",
"host":"0.0.0.0",
"threadCount":"2",
"IsPrintError":"True",
"UnLimitedIP":["*"],
"AsyncTheadCount":"4",
"AsyncTimeOut":"20",
"ExitPassword":"123456",
"Database":{
"isUseDB":"False",
"serverip":"10.86.87.79",
"port":"5432",
"dbname":"postgres",
"username":"postgres",
"password":"postgres",
"poolcount":"100",
"isecho":"False"
},
"Logger":{
"Level":"0",
"IsPrint":"True",
"SaveDay":"30"
}
}
}''')
        self.__getSetDict()
        self.__readValue()


    def __writeLog(self, log):
        print(log)

    def __getSetDict(self):
        with open(self.__fileName, 'r') as f:
            jsonStr = f.read()
            json = eval(jsonStr)
        self.__setDict = json
        return self.__setDict

    def __readValue(self):
        try:
            if 'InterfaceModules'in self.__setDict.keys():
                moduleDict = self.__setDict['InterfaceModules']
                for module in moduleDict:
                    self.__interfaceModules.append(module)
            else:
                moduleDict = None
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            serviceModules = self.__setDict['ServiceModules']
            for module in serviceModules:
                self.__serviceModules.append(module)
                self.__ServicesInfo[module] = self.__setDict['ServiceModules'][module]
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            self.__Port = int(self.__setDict['options']['port'])
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            self.__IsDebug = str(self.__setDict['options']['debug']).lower() == 'true'
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            self.__Host = self.__setDict['options']['host']
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            self.__ThreadCount = int(self.__setDict['options']['threadCount'])
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            self.__IsPrintError = str(self.__setDict['options']['IsPrintError']).lower() == 'true'
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            self.__FilePath = self.__setDict['options']['filePath']
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            self.__UnLimitedIP = self.__setDict['options']['UnLimitedIP']
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            if moduleDict:
                for n in moduleDict:
                    self.__HostInfo[n] = self.__setDict['InterfaceModules'][n]#
        except Exception as e:
            self.__writeLog(e)
        #
        #
        try:
            self.__AsyncTheadCount = int(self.__setDict['options']['AsyncTheadCount'])
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            self.__AsyncTimeOut = int(self.__setDict['options']['AsyncTimeOut'])
        except Exception as e:
            self.__writeLog(e)
        #
        try:
            self.__Database = self.__setDict['options']['Database']
        except Exception as e:
            self.__writeLog(e)
    @property
    def Root(self):
        return self.__setDict

    @property
    def Database(self):
        return self.__Database

    @property
    def AsyncTimeOut(self):
        return self.__AsyncTimeOut

    @property
    def AsyncTheadCount(self):
        return self.__AsyncTheadCount

    @property
    def HostInfo(self):
        return self.__HostInfo

    @property
    def ServicesInfo(self):
        return self.__ServicesInfo

    @property
    def UnLimitedIP(self):
        return self.__UnLimitedIP

    @property
    def FilePath(self):
        return self.__FilePath

    @property
    def IsPrintError(self):
        return self.__IsPrintError

    @property
    def ServiceModules(self):
        return self.__serviceModules

    @property
    def InterfaceModules(self):
        return self.__interfaceModules

    @property
    def Port(self):
        return self.__Port

    @property
    def IsDebug(self):
        return self.__IsDebug

    @property
    def Host(self):
        return self.__Host

    @property
    def threadCount(self):
        return self.__ThreadCount



configer = Configer('Config.json')

