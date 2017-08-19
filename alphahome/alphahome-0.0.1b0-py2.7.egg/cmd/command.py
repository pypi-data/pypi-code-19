# -*- coding:utf-8 -*-

import json
import requests
import git
import time
import os
import oss2
import zipfile


class Application(object):
    app = None

    def __init__(self):
        try:
            with open('.alphahome', 'rb') as f:
                self.app = json.loads(f.read())
        except IOError as e:
            pass

        if self.is_bind():
            flag, name = self.auth(self.app.get('appid'), self.app.get('secret'))
            if not flag:
                self.app = None

    def bind(self):
        """
        绑定当前应用至网络
        :return:
        """
        if self.app is not None:
            print(u"当前应用已绑定，是否覆盖当前绑定的应用？[Y|n]")
            if not raw_input() in ['Y', 'y']: return

        print(u"[绑定] 请输入应用相关信息，具体信息可以在AlphaHome开放平台中查询")
        for i in range(3):
            appid = raw_input(u"appid: ")
            secret = raw_input(u"secret: ")
            print(u"正在验证应用信息中...")
            flag, name = self.auth(appid, secret)
            if not flag:
                print(u"验证失败，请重新输入")
            else:
                print(u"验证成功")
                self.storage(appid, secret)
                print u"绑定成功，应用名为 【{}】".format(name)
                break
        else:
            print(u"三次验证失败！")
            return

    def upload(self):
        """
        提交代码到git仓库
        :return:
        """
        print('正在验证绑定...')
        if not self.is_bind() or not self.auth(self.app.get('appid'), self.app.get('secret')):
            print("当前应用没有成功绑定，请返回先绑定")
            return
        print('验证绑定成功')
        print('正在提交仓库...')
        file_list = []
        with open('INCLUDING', 'rb') as f:
            file_list = [f.strip() for f in f.readlines() if f.strip() != '']

        zipFile = zipfile.ZipFile(r'.temp.zip', 'w')
        for f in file_list:
            zipFile.write(f, f, zipfile.ZIP_DEFLATED)
        zipFile.close()
        print('打包成功，打包了{}个文件'.format(file_list.__len__()))

        remote_file = self.app.get('appid')

        auth = oss2.Auth('LTAI88zhu6Pl0NGD', 'PWVjKLGu99t2TVbjcQlgzENVmKEKjZ')
        bucket = oss2.Bucket(auth, 'oss-cn-beijing.aliyuncs.com', 'alphahome-project')

        exist = bucket.object_exists(remote_file)
        if exist:
            bucket.delete_object(remote_file)

        bucket.put_object_from_file(remote_file, '.temp.zip')

        print('提交成功')

    def is_bind(self):
        """
        当前应用是否已绑定
        :return:
        """
        return self.app is not None and self.app.get('appid') is not None and self.app.get('secret') is not None

    def auth(self, appid, secret):
        auth_url = u"https://api.alphaho.me/open/application-auth/"
        res = requests.post(auth_url, data=dict(appid=appid, secret=secret)).text
        try:
            res = json.loads(res)
            if res[u"flag"]:
                return True, res[u"name"]
            else:
                return False, None
        except Exception as e:
            print(u"验证失败，请检查网络连接！")
            raise e

    def storage(self, appid, secret):
        data = json.dumps(dict(appid=appid, secret=secret))
        with open('.alphahome', 'wb') as f:
            f.write(data)
