from setuptools import setup, find_packages
import sys

extra = {}
if sys.version_info >= (3,):
    extra['use_2to3'] = True

setup(name="python3-smpplib",
      version='1.0.22',
      description='SMPP library for python (fork https://github.com/podshumok/python-smpplib',
      packages=find_packages(),
      zip_safe=True,
      classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Topic :: Communications :: Telephony',
        'Intended Audience :: Telecommunications Industry',
        'License :: OSI Approved',
        ],
      **extra
)
