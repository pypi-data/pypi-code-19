from setuptools import setup

setup(name='mcazurerm',
      version='0.1.2',
      description='Azure Resource Manager REST wrappers',
      url='http://github.com/pjshi23/mcazurerm',
      author='Stan Peng',
      author_email='pjshi23@gmail.com',
      license='MIT',
      packages=['mcazurerm'],
      install_requires=[
          'adal',
          'requests',
      ],
      zip_safe=False)
