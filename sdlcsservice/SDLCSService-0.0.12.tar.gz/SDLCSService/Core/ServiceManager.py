
import multiprocessing
import os
import sys
import threading

from .Config import configer
from .Connection import PostgresConnection

from .Logger import logger


class ServiceManager(object):
    __modules = []
    __threadingPool = []

    def __init__(self):
        self.configer = configer
        self.__initAppPath()
        self.__bingdingService()
        self.__start()

    def __bingdingService(self):
        for sm in configer.ServiceModules:
            path = os.getcwd() + '/ServiceMoudels/' + sm + '/' + sm + '.py'
            if not os.path.exists(path):
                logger.info('服务[' + sm + ']路径' + path + '不存在！')
                continue
            module = __import__(sm)
            moduleInstance = getattr(module, sm)()
            isUseDB = str(configer.Database['isUseDB']).lower() == 'true'
            if isUseDB:
                moduleInstance.connection = PostgresConnection()
            moduleInstance.logger = logger
            moduleInstance.DataPath = configer.FilePath + sm + '/'
            moduleInstance.configer = configer.ServicesInfo[sm]
            moduleInstance.name = sm
            moduleInstance.loopTime = float(configer.ServicesInfo[sm]['loopTime'])
            queue = multiprocessing.Queue()
            moduleInstance.queue = queue
            self.__modules.append((moduleInstance,sm,queue))

    def __initAppPath(self):
        for moduleName in self.configer.ServiceModules:
            sys.path.append(
                os.getcwd() + '/ServiceMoudels/' + moduleName
            )

    def __start(self):
        for instance in self.__modules:
            pr = multiprocessing.Process(target=instance[0].processMain,args=())
            self.__threadingPool.append(pr)
            pr.daemon = True
            pr.queue = instance[2]
            pr.start()
            logger.info('服务模块[' + instance[1] + '] 启动...')

    @classmethod
    def Stop(cls):
        logger.info('接收到退出命令,请等待各模块退出...')
        for pr in cls.serviceManager.__threadingPool:
            pr.queue.put('end')
            pr.terminate()

    @classmethod
    def delayInit(cls):
        import time
        time.sleep(2)
        cls.serviceManager = ServiceManager()

    @classmethod
    def init(cls):
        t = threading.Thread(target=cls.delayInit,args=())
        t.start()





