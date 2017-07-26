#!/usr/bin/env python
# -*- coding: utf-8 -*-
import subprocess
import os
import webbrowser

import shutit

from agent.util.file import (
    download,
    work_dir
)
from ..config import macaca
import agent.qualityplatform.agent as api
from ..consts import (
    TaskType,
    DeviceStatus
)


class Macaca(object):
    def __init__(self, task_id, data):
        self.task_id = task_id
        self.data = data
        self.task_type = data.get('task_type')
        self.devices_id = data.get('devices_id')
        self.macaca_dir = work_dir(os.getcwd() + '/agent/macaca')
        os.chdir(self.macaca_dir)
        self.devices = str(self.devices_id).split(',')
        self.__connect_devices()

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
        self.case_url = self.data.get('case_url')
        case_dir = 'task'
        file_name = str(self.task_id) + '.js'
        download(case_dir, file_name,
                 self.case_url)
        subprocess.call('macaca run -p 4444 -d ' + case_dir + '/' +
                        file_name, shell=True)
        self.__disconnect_devices()

    def __ui_record(self):
        if not macaca['isMacacaServerAlive']:
            subprocess.Popen("macaca server --port 4444 --verbose", shell=True)
            macaca['isMacacaServerAlive'] = True

        self.test_case_id = self.data.get('test_case_id')
        self.app_url = self.data.get('app_url')
        case_dir = 'sample/' + str(self.task_id) + '/' + str(self.test_case_id) + '.js'
        app_url = self.app_url.encode('utf-8')

        session = shutit.create_session('bash')
        session.send('uirecorder --mobile', expect='测试脚本文件名', echo=True)
        session.send(case_dir, expect='App路径', echo=True)
        session.send(app_url, echo=True, check_exit=False)
        self.__disconnect_devices()
        case_file = open(case_dir, 'rb')
        api.upload_case_file(self.test_case_id, case_file)

    def __connect_devices(self):
        for device_id in self.devices:
            device = api.get_device_by_id(device_id)
            ip = device.get('ip')
            subprocess.call('adb connect ' + ip, shell=True)
            api.update_device_status(device_id, DeviceStatus.offline.value)

    def __disconnect_devices(self):
        for device_id in self.devices:
            device = api.get_device_by_id(device_id)
            ip = device.get('ip')
            subprocess.call('adb disconnect ' + ip, shell=True)
            api.update_device_status(device_id, DeviceStatus.online.value)

    def __reports(self):
        webbrowser.open_new(self.macaca_dir + "/reports/index.html")
