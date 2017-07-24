#-*- encoding: UTF-8 -*-
import io

from setuptools import find_packages
from setuptools import setup

VERSION = '0.2.0'

with io.open("README.md", encoding="utf8") as f:
    readme = f.read()

install_requires = open("requirement.txt").readlines()

setup(
    name="zhihu",  # pip 安装时用的名字
    version=VERSION,  # 当前版本，每次更新上传到pypi都需要修改
    author="liuzhijun",
    author_email="lzjun567@gmail.com",
    url="https://github.com/lzjun567/zhihu-api",
    packages=find_packages(),
    keyworads="zhihu",
    description="zhihu api from humans",
    long_description=readme,
    # packages=[
    #     "zhihu",
    #     "zhihu.models"
    # ],
    include_package_data=True,
    license='MIT License',
    classifiers=[],
    install_requires=install_requires,
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        "pytest",
    ]
)
