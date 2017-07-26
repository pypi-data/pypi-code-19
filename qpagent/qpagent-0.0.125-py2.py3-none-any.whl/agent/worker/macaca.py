#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import webbrowser
import json

import shutit

from agent.util.file import (
    download,
    work_dir
)
from ..config import macaca
import agent.qualityplatform.agent as api
from ..consts import TaskType


class Macaca(object):
    def __init__(self, data):
        print(data)
        # self.data = json.loads(data)
        self.data = data
        self.task_type = data.get('task_type')
        self.devices_id = data.get('devices_id')
        self.macaca_dir = work_dir(os.getcwd() + '/agent/macaca')
        os.chdir(self.macaca_dir)
        self.devices = self.devices_id.split(',')
        for device in self.devices:
            subprocess.call('adb connect ' + device, shell=True)
            api.update_device_status(device, 1)

        if not macaca['isMobileUIRecorderInit']:
            session = shutit.create_session('bash')
            session.send('uirecorder init --mobile', expect='WebDriver域名或IP', echo=True)
            session.send('127.0.0.1', expect='WebDriver端口号', echo=True)
            session.send('4444', echo=True, check_exit=False)
            macaca['isMobileUIRecorderInit'] = True

    def run(self):
        if self.task_type is TaskType.uiplay.value:
            self.__ui_play()
        elif self.task_type is TaskType.uirecord.value:
            self.__ui_record()

    def __ui_play(self):
        self.app_name = self.__post_get('app_name', self.data)
        self.version_name = self.__post_get('version_name', self.data)
        self.module_name = self.__post_get('module_name', self.data)
        self.case_name = self.__post_get('case_name', self.data)
        self.case_url = self.__post_get('case_url', self.data)
        case_dir = self.macaca_dir + '/' + self.app_name + '/' + self.version_name + '/' + self.module_name
        file_name = self.case_name + '.js'
        download(case_dir, file_name,
                 self.case_url)
        subprocess.call('macaca run -p 4444 -d ' + case_dir + '/' +
                        file_name, shell=True)
        self.__disconnect_devices()

    def __ui_record(self):
        if not macaca['isMacacaServerAlive']:
            subprocess.Popen("macaca server --port 4444 --verbose", shell=True)
            macaca['isMacacaServerAlive'] = True

        self.app_name = self.__post_get('app_name', self.data)
        self.app_version_id = self.__post_get('app_version_id', self.data)
        self.module_id = self.__post_get('module_id', self.data)
        self.version_name = self.__post_get('version_name', self.data)
        self.module_name = self.__post_get('module_name', self.data)
        self.case_name = self.__post_get('case_name', self.data)
        self.app_url = self.__post_get('app_url', self.data)
        case_dir = self.app_name + '/' + self.version_name + '/' + self.module_name + '/' + self.case_name + '.js'

        case_name = case_dir.encode('utf-8')
        app_url = self.app_url.encode('utf-8')
        session = shutit.create_session('bash')
        session.send('uirecorder --mobile', expect='测试脚本文件名', echo=True)
        session.send(case_name, expect='App路径', echo=True)
        session.send(app_url, echo=True, check_exit=False)
        self.__disconnect_devices()
        # case_file = open(case_dir, 'r')
        # qualityplatform.upload_case_file(self.app_name, self.app_version_id, self.module_id, case_file)

    def __disconnect_devices(self):
        for device in self.devices:
            subprocess.call('adb disconnect ' + device, shell=True)
            api.update_device_status(device, 0)

    def __reports(self):
        webbrowser.open_new(self.macaca_dir + "/reports/index.html")

    def __post_get(self, name, data):
        return data[name]
