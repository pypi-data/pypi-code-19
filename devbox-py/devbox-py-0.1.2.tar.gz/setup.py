from setuptools import setup
import sys
import os
import subprocess
import devbox
from setuptools.command.develop import develop
from setuptools.command.install import install


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        # PUT YOUR POST-INSTALL SCRIPT HERE or CALL A FUNCTION
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)

setup(name='devbox-py',
      description='DevBox for Python - Managing environments and boilerplates.',
      version='0.1.2',
      author='D. Misic',
      author_email='dion@gmail.com',
      packages=['devbox'],
      license='MIT',
      cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
        },
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
         'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
    ],
)
