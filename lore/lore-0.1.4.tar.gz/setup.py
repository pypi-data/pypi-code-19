# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install
import os
import subprocess
import sys
if sys.version_info.major == 2:
    from urllib import urlopen
elif sys.version_info.major == 3:
    from urllib.request import urlopen

import lore
from lore import ansi, util


class LoreInstallCommand(install):
    def run(self):
        install.run(self)
        LoreInstallCommand.setup_pyenv()

    @staticmethod
    def setup_pyenv():
        pyenv = util.which('pyenv')
        if not pyenv:
            pyenv = os.path.join(os.environ['HOME'], '.pyenv', 'bin', 'pyenv')
            if not os.path.exists(pyenv):
                pyenv = None

        if pyenv:
            print(ansi.success('FOUND') + ' pyenv')
            return
        
        if os.name == 'nt':
            print(
                ansi.warning() + ' pyenv does not '
                'support Windows. You\'ll have the unfortunate task of managing'
                ' python versions yourself 😰'
            )
            return
        
        print(ansi.success('INSTALLING') + ' pyenv')
        url = (
            'https://raw.githubusercontent.com/'
            'pyenv/pyenv-installer/master/bin/pyenv-installer'
        )
        subprocess.Popen(('bash', '-c', urlopen(url).read())).wait()
        subprocess.check_call((
            'git',
            'clone',
            'https://github.com/pyenv/pyenv-virtualenv.git',
            '$(pyenv root)/plugins/pyenv-virtualenv)'
        ))


def readme():
    with open('README.rst', 'r') as f:
        return f.read()

setup(
    name='lore',
    version=lore.__version__,
    description='a framework for building and using data science',
    long_description=readme(),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*, <4',
    keywords='machine learning framework tensorflow airflow',
    url='http://github.com/instacart/lore',
    author='Montana Low',
    author_email='montana@instacart.com',
    license='MIT',
    packages=['lore'],
    install_requires=[
        'smart-open',
        'keras',
        'tensorflow',
        'scikit-learn',
        'h5py',
        'numpy',
        'pandas',
        'virtualenv',
        'virtualenvwrapper',
        'python-dotenv',
        'jupyter',
        'ipykernel',
        'dill'
    ],
    zip_safe=True,
    test_suite='tests',
    tests_require=[],
    cmdclass={
        'install': LoreInstallCommand,
    },
    entry_points={
        'console_scripts': [
            'lore=lore.__main__:main',
        ],
    },
)
