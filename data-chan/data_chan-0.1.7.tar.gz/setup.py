from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()
        
        
setup(name='data_chan',
      version='0.1.7',
      description='Python bindings for Data-Chan',
      long_description=readme(),
      url='https://github.com/fermiumlabs/data-chan-python/',
      author='Fermium LABS',
      author_email='info@fermiumlabs.com',
      license='MIT',
      packages=['data_chan'],
      zip_safe=False,
      include_package_data=True,
      )
