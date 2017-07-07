#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import webbrowser
import json

from slave.util.file import File_Downloader


class MacacaWorker(object):
    def __init__(self, macaca_dir, data):
        self.data = json.loads(data)
        self.macaca_type = self.__post_get('task_type', self.data)
        self.macaca_dir = macaca_dir
        subprocess.Popen("macaca server --port 4444 --verbose", shell=True)
        os.chdir(self.macaca_dir)
        subprocess.call('uirecorder init --mobile', shell=True)

    def run(self):
        if self.macaca_type == 1:
            self.__run_macaca_test()
        elif self.macaca_type == 2:
            self.__run_uirecorder()

    def __run_macaca_test(self):
        self.app_name = self.__post_get('app_name', self.data)
        self.version_name = self.__post_get('version_name', self.data)
        self.module_name = self.__post_get('module_name', self.data)
        self.case_name = self.__post_get('case_name', self.data)
        self.case_url = self.__post_get('case_url', self.data)
        case_dir = self.macaca_dir + '/' + self.app_name + '/' + self.version_name + '/' + self.module_name
        file_name = self.case_name + '.js'
        File_Downloader.download(case_dir, file_name,
                                 self.case_url)
        subprocess.call('source run.sh ' + case_dir + '/' +
                        file_name, shell=True)

    def __run_uirecorder(self):
        subprocess.call('uirecorder --mobile', shell=True)

    def __reports(self):
        webbrowser.open_new(self.macaca_dir + "/reports/index.html")

    def __post_get(self, name, data):
        return data[name]
