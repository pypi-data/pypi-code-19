import os
import sys

import threading,time,signal
import multiprocessing
from .FuncHelper import FuncHelper


def myHandler(signum='', frame=''):
    time.sleep(3)
    os.kill(multiprocessing.current_process().pid,signal.SIGINT)

def ExitApplication(request):
    # t = threading.Thread(target=myHandler,args=())
    # t.start()
    return request.Response(text='exit')

class Bindinger(object):
    __modulePath = ''
    __instances = {}
    def __initAppPath(self):
        for moduleName in self.__configer.InterfaceModules:
            sys.path.append(
                os.getcwd() + '/InterfaceMoudels/' + moduleName
            )
        self.__modulePath = os.getcwd() + '/InterfaceMoudels/'
        self.__routerPath = []

    def downLoadStaticFile(self,request):
        path = request.path

        if self.__configer.FilePath.endswith('/'):
            fileName = self.__configer.FilePath + path[1:]
        else:
            fileName = self.__configer.FilePath + path

        if not os.path.exists(fileName):
            return request.Response(code=404, text='Not Found')

        extName = FuncHelper.getFileExtName(path)
        extName = extName.lower()
        if extName == 'jpg':
            mimeTypeStr = 'image/jpeg'
        elif extName == 'html':
            mimeTypeStr = 'text/html'
        elif extName == 'htm':
            mimeTypeStr = 'text/html'
        elif extName == 'txt':
            mimeTypeStr = 'text/html'
        elif extName == 'gif':
            mimeTypeStr = 'image/gif'
        elif extName == 'js':
            mimeTypeStr = 'text/javascript'
        elif extName == 'css':
            mimeTypeStr = 'text/css'
        else:
            mimeTypeStr = 'application/octet-stream'

        with open(fileName,'rb')  as f:
            txt = f.read()
        result = request.Response(body=txt,mime_type = mimeTypeStr,headers={"Accept-Ranges":"bytes","Access-Control-Allow-Origin":"*"})
        return result



    def bindingTransferMethod(self,method):
        def processMethod(request):
            if '*' in self.__configer.UnLimitedIP:
                pass
            else:
                if (not self.__configer.IsDebug) and (not request.remote_addr in self.__configer.UnLimitedIP):
                    self.logger.info('非法连接 ,IP:' + request.remote_addr + ' Path:' + request.path)
                    return request.Response(code=403,text='Forbidden')
            errorCode = 0
            try:
                result = method(request)
                self.logger.info('IP:' + request.remote_addr + ' Path:' + request.path + ' 正常访问')
            except Exception as e:
                self.logger.info('IP:' + request.remote_addr + ' Path:' + request.path + ' 访问出错')
                result = str(e)
                self.logger.error(request.path + '出错：' + str(e))
                errorCode = 1
            if errorCode == 1:
                return request.Response(text='error:' + result)
            else:
                return result
        return processMethod

    def bindingSetting(self,moduleInstance,moduleConfig):
        moduleInstance.configer = moduleConfig

    def bindingMethod(self,moudelName,subMouduleName):
        module = __import__(subMouduleName)
        moduleInstance = getattr(module, subMouduleName)()
        methods = dir(moduleInstance)
        moduleInstance.logger = self.logger
        moduleInstance.connection = self.connection
        moduleInstance.DataPath = self.__configer.FilePath + moudelName + '/'
        self.__instances[subMouduleName] = moduleInstance
        moduleInstance.allModules = self.__instances
        self.bindingSetting(moduleInstance,self.__configer.HostInfo[moudelName])
        for methodName in methods:
            if (methodName.startswith('__') or
                methodName.startswith('_')):
                pass
            else:
                method = getattr(moduleInstance,methodName)
                methodPath = '/' + moudelName[4:] + '/' + methodName
                if methodPath in self.__routerPath:
                    self.logger.info('同步方法[' + methodPath + ']重复')
                    continue
                self.__routerPath.append(methodPath)
                self.__router.add_route(methodPath,self.bindingTransferMethod(method))
                if self.__configer.IsDebug:
                    print(methodPath)

    def getSubMouduleList(self,moudelName):
        subMoudules = []
        filePath = self.__modulePath + moudelName
        if not os.path.isdir(filePath):
            self.logger.info('模块[' + moudelName + ']路径不正确！')
            return subMoudules
        filelist = os.listdir(filePath)
        for f in filelist:
            if f.startswith(moudelName) and f.endswith('.py'):
                subMoudules.append(f[:f.find('.')])
        return subMoudules


    def bindingClass(self):
        moudels = self.__configer.InterfaceModules
        for moudelName in moudels:
            if moudelName == 'SDLCTester' and (not self.__configer.IsDebug):
                continue
            subMoudules = self.getSubMouduleList(moudelName)
            for sm in subMoudules:
                self.bindingMethod(moudelName,sm)


    def BindingRouter(self,router,configer,logger,connection):
        self.connection = connection
        self.__router = router
        self.__configer = configer
        self.logger = logger
        self.__initAppPath()
        self.bindingClass()
        self.__router.add_route('/exit/' + configer.Root['options']['ExitPassword'],ExitApplication)
        self.__router.add_route('/static/{p1}', self.bindingTransferMethod(self.downLoadStaticFile))
        self.__router.add_route('/static/{p1}/{p2}', self.bindingTransferMethod(self.downLoadStaticFile))
        self.__router.add_route('/static/{p1}/{p2}/{p3}', self.bindingTransferMethod(self.downLoadStaticFile))


bindinger = Bindinger()

if __name__ == '__main__':
    filelist = os.listdir('/root/work/AutoTest/InterfaceMoudels/SDLCJenkins')

