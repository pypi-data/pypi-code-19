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


class MobileUiRecorderWorker(object):
    def __init__(self, macaca_dir, data):
        print(macaca_dir)
        print(data)
        self.data = json.loads(data)
        self.macaca_type = self.__post_get('task_type', self.data)
        self.devices_ip = self.__post_get('devices_ip', self.data)
        self.macaca_dir = macaca_dir
        os.chdir(self.macaca_dir)
        self.devices = self.devices_ip.split(',')
        for device in self.devices:
            print(device)
            subprocess.call('adb connect ' + device, shell=True)
            api.update_device_status(device, 1)

        print('>>>>>>>>>>>>>')
        if not config['isMobileUIRecorderInit']:
            session = shutit.create_session('bash')
            session.send('uirecorder init --mobile', expect='WebDriver域名或IP', echo=True)
            session.send('127.0.0.1', expect='WebDriver端口号', echo=True)
            session.send('4444', echo=True, check_exit=False)
            config['isMobileUIRecorderInit'] = True

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
        subprocess.call('macaca run -p 4444 -d ' + case_dir + '/' +
                        file_name, shell=True)
        self.__disconnect_devices()

    def __run_uirecorder(self):
        self.app_name = self.__post_get('app_name', self.data)
        self.app_version_id = self.__post_get('app_version_id', self.data)
        self.module_id = self.__post_get('module_id', self.data)
        self.version_name = self.__post_get('version_name', self.data)
        self.module_name = self.__post_get('module_name', self.data)
        self.case_name = self.__post_get('case_name', self.data)
        self.app_url = self.__post_get('app_url', self.data)
        case_dir = self.app_name + '/' + self.version_name + '/' + self.module_name + '/' + self.case_name + '.js'
        print(case_dir)

        session = shutit.create_session('bash')
        session.send('uirecorder --mobile', expect='测试脚本文件名', echo=True)
        session.send('eleme/android.js', expect='App路径', echo=True)
        session.send(self.app_url, echo=True, check_exit=False)

        self.__disconnect_devices()
        # case_file = open(case_dir, 'r')
        # api.upload_case_file(self.app_name, self.app_version_id, self.module_id, case_file)

    def __disconnect_devices(self):
        for device in self.devices:
            subprocess.call('adb disconnect ' + device, shell=True)
            api.update_device_status(device, 0)

    def __reports(self):
        webbrowser.open_new(self.macaca_dir + "/reports/index.html")

    def __post_get(self, name, data):
        return data[name]
