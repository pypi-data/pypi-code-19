import os
import subprocess

class Language(object):
    _FORMAT = []

    def __init__(self, fullpath):
        self.fullpath = fullpath
        self.path, _ = os.path.split(fullpath)

    @classmethod
    def format(cls):
        return cls._FORMAT

    def compile(self):
        '''compile 接口'''
        raise NotImplementedError('The inheritance class must implement {} interface'.format('compile'))

class Python(Language):
    _FORMAT = ['.py']

    def compile(self):

        p = subprocess.Popen('/usr/bin/python {}'.format(self.fullpath), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        stdout, errors = p.communicate()
        print(str(stdout, encoding='utf-8')) if stdout else None
        print(str(errors,  encoding='utf-8')) if errors else None


class Cpp(Language):
    _FORMAT = ['.cpp']

    def compile(self):
        print("Compile C++")
