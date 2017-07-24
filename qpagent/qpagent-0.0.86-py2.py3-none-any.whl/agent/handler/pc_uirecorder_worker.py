#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import webbrowser
import json

import shutit

from agent.util.file import File_Downloader
from agent.config import config
import agent.api.httpizza as api


class PCUiRecorderWorker(object):
    def __init__(self, macaca_dir, data):
        self.data = json.loads(data)
        self.macaca_type = self.__post_get('task_type', self.data)
        self.macaca_dir = macaca_dir
        os.chdir(self.macaca_dir)

        if not config['isPCUIRecorderInit']:
            session = shutit.create_session('bash')
            session.send('uirecorder init', expect='Path扩展属性配置,除id,name,class之外', echo=True)
            session.send('', expect='属性值黑名单正则', echo=True)
            session.send('', expect='断言前隐藏', echo=True)
            session.send('', expect='WebDriver域名或IP', echo=True)
            session.send('', expect='WebDriver端口号', echo=True)
            session.send('', expect='需要同时测试的浏览器列表', echo=True)
            session.send('chrome', echo=True, check_exit=False)
            config['isPCUIRecorderInit'] = True

    def run(self):
        if self.macaca_type == 1:
            self.__run_macaca_test()
        elif self.macaca_type == 2:
            self.__run_uirecorder()

    def __run_macaca_test(self):
        self.module_name = self.__post_get('module_name', self.data)
        self.case_name = self.__post_get('case_name', self.data)
        self.case_url = self.__post_get('case_url', self.data)
        case_dir = self.module_name
        file_name = self.case_name + '.js'
        File_Downloader.download(case_dir, file_name,
                                 self.case_url)
        subprocess.call('source run.sh ' + case_dir + '/' +
                        file_name, shell=True)

    def __run_uirecorder(self):
        self.module_id = self.__post_get('module_id', self.data)
        self.module_name = self.__post_get('module_name', self.data)
        self.case_name = self.__post_get('case_name', self.data)
        case_dir = self.module_name + '/' + self.case_name + '.js'

        session = shutit.create_session('bash')
        session.send('uirecorder', expect='测试脚本文件名', echo=True)
        session.send(case_dir, expect='打开同步校验浏览器', echo=True)
        session.send('', expect='浏览器大小', echo=True)
        session.send('', echo=True, check_exit=False)

        # case_file = open(case_dir, 'r')
        # api.upload_case_file(self.module_id, case_file)

    def __reports(self):
        webbrowser.open_new(self.macaca_dir + "/reports/index.html")

    def __post_get(self, name, data):
        return data[name]
