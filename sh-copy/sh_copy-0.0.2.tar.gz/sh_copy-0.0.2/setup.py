# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='sh_copy',
    version='0.0.2',
    description=(
        '文件复制，简单的一个方法，用来测试一下公共包'
    ),
    long_description=open('README.rst').read(),
    author='hnf',
    author_email='369685930@qq.com',
    maintainer=' hnf',
    maintainer_email=' 369685930@qq.com',
    license='BSD License',
    packages=find_packages(),  #  申明你的包里面要包含的目录，比如  ['mypackage', 'mypackage_test']  可以是这种使用我的示例，让setuptools自动决定要包含哪些包
    platforms=["all"],
    url='https://github.com/Haner27/sh_copy.git',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries'
    ]
)
