"""

This is a python-based installer for the lal, which is a
component of lalsuite.

Installer Maintainer: Daniel Williams <daniel.williams@ligo.org>

"""


try:
    from setuptools import setup
    from setuptools.command.install import install as SetuptoolsInstall
except ImportError:
    from distutils.core import setup

from subprocess import call
import os

from setuptools.command.install import install as SetuptoolsInstall
from distutils.command.build import build

try:
    virtualenv =  os.environ['VIRTUAL_ENV']
    print("This installation is being completed within a virtual environment at {}".format(virtualenv))
except KeyError:
    virtualenv = None



class LALInstall(SetuptoolsInstall):
    def run(self):
        SetuptoolsInstall.run(self)
        os.chdir("lal")
        call(["make", "install", "--silent"])
        os.chdir("..")

class LALBuild(build):
    def run(self):
        """
        Run the configure > make pipeline for LAL
        """
        os.chdir("lal")
        if virtualenv:
            call(["bash", "configure", "--silent", "--enable-silent-rules", "--prefix=/{}".format(virtualenv), "--enable-swig-python"])
        else:
            call(["bash", "configure", "--silent", "--enable-silent-rules", "--enable-swig-python"])
        call(["make",  "-j", "--silent"])
        os.chdir("..")

        
requirements = ["numpy"]

        
setup(
    name='GWlal',
    version='0.0.2',
    description="A Pythonic installer for lal - part of lalsuite",
    # long_description=readme + '\n\n' + history,
    author="LIGO Scientific Collaboration / Virgo Collaboration",
    author_email='daniel.williams@ligo.org',
    url='https://git.ligo.org/daniel-williams/python-ligo',
    packages=[
         'lal',
    ],
    package_dir={'lal': 'lal'},
    install_requires=requirements,
    cmdclass={'install': LALInstall, 'build': LALBuild},
    # license="GPLv3",
    zip_safe=True,
    keywords='ligo gravitational-waves',
    # classifiers=[
    #     'Development Status :: 3 - Alpha',
    #     'Intended Audience :: Science/Research',
    #     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    #     'Natural Language :: English',
    #     'Programming Language :: Python :: 3',
    #     'Programming Language :: Python :: 3.3',
    #     'Programming Language :: Python :: 3.4',
    #     'Programming Language :: Python :: 3.5',
    # ]
)
