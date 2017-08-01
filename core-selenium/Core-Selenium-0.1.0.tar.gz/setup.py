'''
Created on Jul 28, 2017

@author: khoi.ngo
'''
from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='Core-Selenium',
      version='0.1.0',
      description='Selenium framework source code',
      long_description=readme(),
      url='http://tfs.logigear.com/SD/SeleniumCore/_git/PythonSeleniumCore',
      keywords='selenium core ngo anh khoi',
      author='Khoi Ngo',
      author_email='quainhan100@gmail.com',
      license='MIT',
      packages=['main', 'resources', 'main.com_logigear', 'main.com_logigear.constant',
                'main.com_logigear.driver', 'main.com_logigear.driver.browser',
                'main.com_logigear.driver.cloud', 'main.com_logigear.driver.mobile',
                'main.com_logigear.element', 'main.com_logigear.element.common'],
      include_package_data=True,
      zip_safe=False)