from setuptools import setup
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages
setup(name='mrlpy',
      version='1.0.0',
      description='Python API to MyRobotLab',
      url='http://github.com/AutonomicPerfection/mrlpy',
      author='AutonomicPerfectionist',
      author_email='bwtbutler@hotmail.com',
      license='GPL',
      packages=find_packages(),
      install_requires=['requests', 'websocket-client'],
      zip_safe=False)
