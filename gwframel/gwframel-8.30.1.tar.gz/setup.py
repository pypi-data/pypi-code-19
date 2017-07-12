"""

This is a python-based installer for the libFrame library, which is a
prerequisite for installing lalsuite.

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


try:
    virtualenv =  os.environ['VIRTUAL_ENV']
    print("This installation is being completed within a virtual environment at {}".format(virtualenv))
except KeyError:
    virtualenv = None

def install_framelib():
    """
    Run the configure > make pipeline for the framelibrary
    """
    os.chdir("src")
    #print "Run the FrameL Bootstrap"
    #call(["autoreconf", "--install"])
    #print "Run the FrameL Configuration"
    if virtualenv:
        call(["bash", "configure", "--silent", "--enable-silent-rules", "--prefix=/{}".format(virtualenv)])
    else:
        call(["bash", "configure", "--silent", "--enable-silent-rules"])
    #print "Making FrameL"
    call(["make",  "-j", "--silent"])
    print "Installing FrameL"
    call(["make", "install", "--silent"])
    os.chdir("../../")

class MyInstall(SetuptoolsInstall):
    def run(self):
        SetuptoolsInstall.run(self)
        install_framelib()

requirements = []
        
setup(
    name='gwframel',
    version='8.30.1',
    description="A Pythonic installer for the GW FrameL library.",
    # long_description=readme + '\n\n' + history,
    author="LIGO Scientific Collaboration, Virgo Collaboration",
    author_email='daniel.williams@ligo.org',
    url='https://git.ligo.org/daniel-williams/python-ligo',
    packages=[
         'gwframel',
    ],
    package_dir={'gwframel':
                 'src'},
    install_requires=requirements,
    cmdclass={'install': MyInstall},
    #license="GPLv3",
    zip_safe=True,
    #keywords='ligo gravitational-waves',
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
