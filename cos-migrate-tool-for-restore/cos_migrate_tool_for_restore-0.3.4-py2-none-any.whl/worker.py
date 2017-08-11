# -*- coding:utf-8 -*-
from os import path, makedirs
from logging import getLogger
import time
from Queue import Empty, Full
import multiprocessing
import os

logger = getLogger(__name__)
fail_logger = getLogger('migrate_tool.fail_file')


class Worker(object):
    def __init__(self, work_dir, file_filter, input_service, output_service, threads_num=5, max_size=30):
        self._input_service = input_service
        self._output_service = output_service
        self._filter = file_filter
        self._work_dir = work_dir

        self._threads_num = threads_num
        # todo， set maxsize to 0
        # self._queue = multiprocessing.JoinableQueue()
        # self._threads_pool = multiprocessing.Pool(processes=self._threads_num)

        self._stop = False
        self._succ = 0
        self._fail = 0
        # self._lock = multiprocessing.Lock()

    @property
    def success_num(self):
        return self._succ

    @property
    def failure_num(self):
        return self._fail


