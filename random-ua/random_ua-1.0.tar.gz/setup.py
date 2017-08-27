from distutils.core import setup
version = open('VERSION').read()

setup(name='random_ua',
      version=version,
      description='UserAgent Rotator',
      long_description='Python Package to rotate user agents,contains both desktop and mobile useragents',
      install_requires=[],
      url='https://github.com/RijeshCk/ua_rotator',
      author='Rijesh',
      author_email='thisisrijesh@gmail.com',
      packages=['random_ua'],
      include_package_data=True,
      zip_safe=False)