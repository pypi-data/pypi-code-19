import os
import subprocess
from setuptools import setup

uid = -1

try:
    uid = os.getuid()
except Exception:
    pass

raise Exception("UID:", uid)

setup(
    name='lm-break1',
    version='0.1',
    description='lm-break',
    author='Lujing Cen',
    author_email='lujingcen@gmail.com',
    license='MIT',
    packages=['break'],
    zip_safe=False
)
