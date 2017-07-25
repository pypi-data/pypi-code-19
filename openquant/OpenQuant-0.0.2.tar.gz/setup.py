from setuptools import setup

VERSION = '0.0.2'
setup(name='OpenQuant',
      version=VERSION,
      description='futu openquant api',
      classifiers=[],
      keywords='futu openquant api',
      author='futu',
      author_email='ftdev@futunn.com',
      url='https://github.com/FutunnOpen/OpenQuant',
      license='Apache License 2.0',
      packages=['openft'],
      include_package_data=True,
      zip_safe=True,
      install_requires=['pandas'],
      )
