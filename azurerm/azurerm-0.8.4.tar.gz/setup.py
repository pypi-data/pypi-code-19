from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='azurerm',
      version='0.8.4',
      description='Azure Resource Manager REST wrappers',
      long_description=readme(),
      url='http://github.com/gbowerman/azurerm',
      author='sendmarsh',
      author_email='guybo@outlook.com',
      license='MIT',
      packages=['azurerm'],
      install_requires=[
          'adal',
          'requests',
      ],
      zip_safe=False)
