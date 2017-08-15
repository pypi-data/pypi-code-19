from setuptools import setup

setup(name='onlinectl',
      version='0.1',
      description='CLI to manage your online.net account',
      url='http://ludoviclogiou.com',
      author='Ludovic Logiou',
      author_email='ludovic.logiou@gmail.com',
      license='MIT',
      packages=['onlinectl'],
      zip_safe=False,
      install_requires=["prettytable==0.7.2","slumber==0.7.1"],
      scripts=[
          'bin/onlinectl'])

