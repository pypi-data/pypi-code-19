from setuptools import setup

setup(name="OpenOPC-Python3x",
      version="1.2.1",
      description=" OPC (OLE for Process Control) toolkit for Python 3.x",
      keywords='python, opc, openopc',
      url='https://github.com/mkwiatkowski/openopc',
      license='GPLv2',
      install_requires=['Pyro4>=4.61'],
      packages = ['src'],
      maintainer = 'Michal Kwiatkowski',
      maintainer_email = 'michal@trivas.pl',
)
