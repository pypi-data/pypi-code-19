#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/8/16 11:31"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
重复检查某应用程序（子命令）标准输出判断其运行状态，若发现吊死则重启。
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, GetCurrentTime, PrintAndSleep, PrintInline
from weberFuncs import GetTimeInteger
import time
import platform
import subprocess
# import psutil
import threading
from winsvFuncs import TerminateByPid


class CCheckStdoutRestart:
    def __init__(self, iShouldOutInSeconds, iShouldEndInSeconds=0, sCoding='gbk'):
        self.iShouldOutInSeconds = iShouldOutInSeconds  # 应在N秒内有输出
        self.iShouldEndInSeconds = iShouldEndInSeconds  # 应在N秒内执行完
        self.sCoding = sCoding  # 输出结果解码
        PrintTimeMsg('CCheckStdoutRestart.iShouldOutInSeconds=(%s)' % self.iShouldOutInSeconds)
        PrintTimeMsg('CCheckStdoutRestart.iShouldEndInSeconds=(%s)' % self.iShouldEndInSeconds)
        PrintTimeMsg('CCheckStdoutRestart.sCoding=(%s)' % self.sCoding)

        self.oProcess = None  # 子进程对象
        self.iTmSubCmdStart = 0 # 获取子进程启动时间
        self.iTmLastStdout = 0  # 获取子进程上次标准输出的时间
        self.isLinux = platform.system() == 'Linux'
        # ON_POSIX = 'posix' in sys.builtin_module_names

    def __handleSubCmdStdout(self, sCmd):
        # 子线程处理子命令标准输出
        while True:
            if self.oProcess:
                for line in iter(self.oProcess.stdout.readline, b''):
                    self.iTmLastStdout = GetTimeInteger()
                    if self.sCoding:  # 从gbk解码到unicode
                        sLine = line.decode(self.sCoding)
                    else:
                        sLine = line
                    PrintInline("   %s" % sLine)
                self.oProcess.stdout.close()
                PrintTimeMsg('ChkCmd(%s).pid=(%s).End <<<' % (sCmd, self.oProcess.pid))
                self.oProcess = None
            else:
                time.sleep(0.001)  #

    def __startSubCmdByPopen(self, sCmd):
        # 启动子命令进程
        self.oProcess = subprocess.Popen(sCmd,
                                         stdin=subprocess.PIPE,
                                         stderr=subprocess.STDOUT,
                                         stdout=subprocess.PIPE,
                                         bufsize=1,
                                         close_fds=self.isLinux)  # ON_POSIX
        # 两个包的 Popen 函数效果一样。
        # self.oProcess = psutil.Popen(sCmd,
        #                              stdin=subprocess.PIPE,
        #                              stderr=subprocess.STDOUT,
        #                              stdout=subprocess.PIPE,
        #                              bufsize=1,
        #                              close_fds=self.isLinux)  # ON_POSIX
        PrintTimeMsg('Popen(%s).pid=(%s).Begin >>>' % (sCmd, self.oProcess.pid))
        self.iTmSubCmdStart = GetTimeInteger()
        self.iTmLastStdout = self.iTmSubCmdStart

    def LoopWaitAndExec(self, sCmd):
        # 启动线程监管子进程运行
        PrintTimeMsg("LoopWaitAndExec.sCmd=(%s)" % sCmd)
        oThread = threading.Thread(target=self.__handleSubCmdStdout, args=(sCmd,))
        oThread.daemon = True  # thread dies with the program
        oThread.start()
        # 主线程，负责启动子进程
        while True:
            self.__startSubCmdByPopen(sCmd)
            while self.oProcess:
                tmNow = GetTimeInteger()
                bQuit = tmNow - self.iTmLastStdout > self.iShouldOutInSeconds
                if not bQuit:
                    if self.iShouldEndInSeconds > 0:
                        bQuit = tmNow - self.iTmSubCmdStart > self.iShouldEndInSeconds
                if bQuit:
                    TerminateByPid(self.oProcess.pid)
                else:
                    time.sleep(0.001)


def mainCCheckStdoutRestart():
    o = CCheckStdoutRestart(10, 8)
    # o.LoopWaitAndExec('ping juchecar.com')  # ok
    # o.LoopWaitAndExec('ping juchecar.com -t')  # ok
    # o.LoopWaitAndExec(['ping', 'juchecar.com', '-t'])  # ok

    o.LoopWaitAndExec('python RunSleep.py')


# --------------------------------------
if __name__ == '__main__':
    mainCCheckStdoutRestart()
