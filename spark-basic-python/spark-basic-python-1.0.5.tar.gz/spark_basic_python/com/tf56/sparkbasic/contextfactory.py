#!/usr/bin/python
# -*- coding: utf-8 -*-

from pyspark import SQLContext, HiveContext
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
import threading

from spark_basic_python.com.tf56.util import configloader

sc_lock = threading.Lock()
sqc_lock = threading.Lock()
stc_lock = threading.Lock()
hc_lock = threading.Lock()
config = configloader.buildconfig("sparkbasic.ini")
'''
CLASS对象: ContextFactory 上下文工厂，构建获取不同组件的上下文
实现模式：采用单例的设计模式实现
'''


class ContextFactory(object):
    # 初始化方法，为了定义类的自变量
    def __init__(self, spark_context=None, sql_context=None,
                 streaming_context=None, hive_context=None):
        self._sc = spark_context
        self._sqc = sql_context
        self._stc = streaming_context
        self._hc = hive_context

    def build_spark_context(self):
        if self._sc is None:
            if sc_lock.acquire():
                if self._sc is None:
                    self._sc = SparkContext(conf=configloader.load("sparkbasic.ini"))
            sc_lock.release()
        return self._sc

    def build_sql_context(self):
        if self._sqc is None:
            if sqc_lock.acquire():
                if self._sqc is None:
                    self._sqc = SQLContext(self.build_spark_context())
            sqc_lock.release()
        return self._sqc

    def build_streaming_context(self):
        if self._stc is None:
            if stc_lock.acquire():
                if self._stc is None:
                    self._stc = StreamingContext(self.build_spark_context(),
                                                 batchDuration=int(config.get("spark", "sparkStream.batchDuration")))
            stc_lock.release()
        return self._stc

    def build_hive_context(self):
        if self._hc is None:
            if hc_lock.acquire():
                if self._hc is None:
                    self._hc = HiveContext(self.build_spark_context())
            hc_lock.release()
        return self._hc
