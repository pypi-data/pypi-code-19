# -*- coding: utf-8 -*-
from distutils.core import setup

setup(name = 'uiautomation',
      version = '1.0.8',
      description = 'Python UIAutomation for Windows',
      license = 'Apache 2.0',
      author = 'yinkaisheng',
      author_email = 'yinkaisheng@foxmail.com',
      url = 'https://github.com/yinkaisheng/Python-UIAutomation-for-Windows',
      platforms = 'Windows Only',
      py_modules = ['uiautomation'],
      data_files = [('Lib/site-packages', ['UIAutomationClient_VC90_X86.dll',
                                           'UIAutomationClient_VC90_X64.dll',
                                           'UIAutomationClient_VC100_X86.dll',
                                           'UIAutomationClient_VC100_X64.dll',
                                           'UIAutomationClient_VC140_X86.dll',
                                           'UIAutomationClient_VC140_X64.dll']
                   )],
      long_description = 'Python UIAutomation for Windows. Supports py2, py3, x86, x64',
      )

