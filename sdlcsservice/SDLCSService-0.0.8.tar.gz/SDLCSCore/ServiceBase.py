import multiprocessing
import time
from abc import abstractmethod

class ServiceBase(object):
    def __init__(self):
        self.__queue = multiprocessing.Queue()

    #消息循环主函数  BASE实现 子类可以直接复写为进程模式
    @abstractmethod
    def processMain(self):
        while True:
            try:
                if self.queue.get(timeout=self.loopTime) == 'end':
                    self.logger.info('服务[' + self.name + ']执行结束!')
                    quit(0)
            except Exception as e:
                pass
            try:
                self.processRequestLoop()
            except Exception as e:
                self.logger.error('服务[' + self.name + ']执行接收出错 错误信息:' + str(e))

            try:
                self.processResponseLoop()
            except Exception as e:
                self.logger.error('服务[' + self.name + ']执行取结果出错 错误信息:' + str(e))

    # 处理过来的请求  各模块自己实现
    @abstractmethod
    def processRequest(self,*args,**kwargs):
        pass

    # 检查结果是否准备 各模块自己实现
    @abstractmethod
    def processResponse(self,*args,**kwargs):
        pass


    #处理过来的请求消息循环  各模块自己实现
    @abstractmethod
    def processRequestLoop(self,*args,**kwargs):
        pass

    #检查结果是否准备好消息循环 各模块自己实现
    @abstractmethod
    def processResponseLoop(self,*args,**kwargs):
        pass

