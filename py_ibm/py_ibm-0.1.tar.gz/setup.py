from setuptools import setup

setup(name='py_ibm',
      version='0.1',
      description='Resources for building individual-based models',
      url='http://github.com/fsfrazao/Py_IBM',
      author='Fabio Frazao',
      author_email='fsfrazao@gmail.com',
      license='GNU General Public License v3.0',
      packages=['py_ibm'],
      install_requires=[
          'numpy',
          ],
      zip_safe=False)
