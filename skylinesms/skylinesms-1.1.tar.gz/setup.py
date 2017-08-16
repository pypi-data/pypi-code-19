from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
  name = 'skylinesms',
  version = '1.1',
  description = 'A module to send sms using the Skyline SMS REST apis, www.skylinesms.com',
  long_description = readme(),
  author = 'Abdu Ssekalala',
  author_email = 'assekalala@gmail.com',
  url = 'https://github.com/assekalala/python-skyline-sms.git',
  keywords = ['sms', 'skyline'],
  py_modules = ['skylinesms'],
  classifiers = [
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
        "Development Status :: 4 - Beta"
  ],
)
