from setuptools import setup

setup(name='ptspeaker',
      version='1.1.0-1',
      description='Initialize the pi-topSPEAKER addon board',
      url='https://pi-top.com',
      author='Pi-Top',
      author_email='deb-maintainer@pi-top.com',
      license='Apache 2.0',
      packages=['ptspeaker'],
      install_requires=[
          'smbus',
      ],
      zip_safe=False)
