from setuptools import setup

setup(name='dispersers',
      version='0.1',
      description='Agent-based models for mechanistic simulations of seed dispersers',
      url='http://github.com/fsfrazao/Dispersers',
      author='Fabio Frazao',
      author_email='fsfrazao@gmail.com',
      license='GNU General Public License v3.0',
      packages=['dispersers'],
      install_requires=[
          'numpy',
          'py_ibm',
          'trees_ibm',
          ],
      zip_safe=False)
