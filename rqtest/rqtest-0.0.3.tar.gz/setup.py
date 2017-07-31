from setuptools import setup, find_packages  # Always prefer setuptools over distutils
from codecs import open  # To use a consistent encoding
from os import path
import subprocess
from setuptools.command.install import install

here = path.abspath(path.dirname(__file__))

class MyInstall(install):
    def run(self):
        print("-- installing... (powered by makecli) --")
        install.run(self)

setup(
        name = 'rqtest',
        version='0.0.3',
        description='test tool based on requests',
        long_description='',
        url='https://github.com/qorzj/rqtest',
        author='qorzj',
        author_email='',
        license='MIT',
        platforms=['any'],

        classifiers=[
            ],
        keywords='rqtest requests',
        packages = ['rqtest'],
        install_requires=['requests'],

        cmdclass={'install': MyInstall},
        entry_points={ },
    )
