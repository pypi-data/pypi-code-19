from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import os

with open('VERSION') as fs:
    VERSION = fs.read().strip()

with open('requirements.txt') as fs:
    REQUIREMENTS = fs.read().strip().split('\n')


def readme():
    with open('README.rst') as fs:
        return fs.read().strip()


# define DevelopHandler and InstallHandler
class DevelopHandler(develop):
    """
    This class handles the develop command.
    """
    def run(self):
        develop.run(self)
        post_setup()


class InstallHandler(install):
    """
    This class handles the install command.
    """
    def run(self):
        install.run(self)
        post_setup()


# TODO: add verbosity
def post_setup():
    # check if the config file is there
    # TODO load a app
    from pyedu.app import app_factory
    app = app_factory('default')

    # install member db
    from pyedu.manage import deploy
    deploy(drop=False)


#  do package setup
setup(name='pyedu',
      description='Leaning Python interactively',
      long_description=readme(),
      author='Mirko Mälicke',
      author_email='mirko@maelicke-online.de',
      version=VERSION,
      license='MIT',
      install_requires=REQUIREMENTS,
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      cmdclass=dict(
          develop=DevelopHandler,
          install=InstallHandler
      )
)
