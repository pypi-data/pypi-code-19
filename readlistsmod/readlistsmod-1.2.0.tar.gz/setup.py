# -*- coding:utf-8 -*-
#从python发布工具中导入setup函数
from distutils.core import setup
setup(
    name =  'readlistsmod',
    version = '1.2.0',
    py_modules = ['readlistsmod'],
    author = 'Hisea',
    author_email = 'hiseamail@foxmail.com',
    url = '',
    description= '对列表进行简单的打印，可根据用户需求，'
                 '默认列表不进行任何缩进操作，除非用户指定'
                 '在显示一行数据前添加level个TAB，'
                 '对内嵌列表进行 level+1 个TAB缩进操作。',
	)
