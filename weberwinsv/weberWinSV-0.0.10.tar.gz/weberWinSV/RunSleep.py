#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
__createTime__ = "2017/8/16 11:57"
__author__ = "WeiYanfeng"
__email__ = "weber.juche@gmail.com"
__version__ = "0.0.1"
        
~~~~~~~~~~~~~~~~~~~~~~~~
程序单元功能描述
测试sleep
~~~~~~~~~~~~~~~~~~~~~~~~
# 依赖包 Package required
# pip install weberFuncs

"""
import sys
from weberFuncs import PrintTimeMsg, PrintAndSleep


def mainRunSleep(iSeconds):
    iLoopCnt = 0
    while True:
        PrintAndSleep(iSeconds, 'mainRunSleep.iLoopCnt=%s' % iLoopCnt)
        iLoopCnt += 1
        if iLoopCnt >= 3:
            break
    PrintTimeMsg('mainRunSleep.End!')


# --------------------------------------
if __name__ == '__main__':
    iSeconds = 5
    mainRunSleep(iSeconds)
