from setuptools import setup

setup(name='qn2-sig',
      version='0.1',
      description='signal processing tools',
      author='Costas Smaragdakis',
      url='http://www.tem.uoc.gr/~kesmarag',
      author_email='kesmarag@gmail.com',
      packages=['qn2.sig'],
      install_requires=['numpy',
                        'PyWavelets'],
      package_dir={'qn2.sig': './'}, )
