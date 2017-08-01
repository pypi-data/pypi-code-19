# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install
import os
import subprocess
import urllib

import lore
from lore import ansi, util


class LoreInstallCommand(install):
    def run(self):
        install.run(self)
        LoreInstallCommand.setup_pyenv()

    @staticmethod
    def setup_pyenv():
        if util.which('pyenv'):
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
        print(
            ansi.warning() + ' you must '
            '`source ~/.profile` after adding pyenv config to have a fully '
            'functional lore installation'
        )
        url = (
            'https://raw.githubusercontent.com/'
            'pyenv/pyenv-installer/master/bin/pyenv-installer'
        )
        subprocess.Popen(('bash', '-c', urllib.urlopen(url).read())).wait()

        home = os.environ.get('HOME')
        shims = (
            '\n# Load pyenv shims\n'
            'export PATH="%s/.pyenv/bin:$PATH"\n'
            'eval "$(pyenv init -)"\n'
        ) % home
        LoreInstallCommand.add_shims(shims, 'pyenv')
    
    @staticmethod
    def add_shims(shims, package):
        home = os.environ.get('HOME')
        shell = os.environ.get('SHELL', '')
        profile = None
        if 'bash' in shell:
            profile = os.path.join(home, '.bash_profile')
            if not os.path.exists(profile):
                profile = os.path.join(home, '.bashrc')
        if not os.path.exists(profile) and 'zsh' in shell:
            profile = os.path.join(home, '.zshrc')
        if not os.path.exists(profile):
            profile = os.path.join(home, '.profile')
        if not os.path.exists(profile):
            print(
                ansi.error() + ' shell profile '
                'could not be found. You will need to manually add the '
                'following for %s shims to work in your shell:\n\n'
                % package
            )
            print(shims)
            return
    
        with open(profile, 'a+') as f:
            f.seek(0)
            content = f.read()
            if package not in content:
                f.write(shims)
                print(
                    ansi.success('UPDATE') + ' the following %s shims '
                    'were added to: %s\n%s' % (package, profile, shims)
                )
                print(
                    ansi.warning() + ' to use %s '
                    'in your current shell, you must run:\n  $ source %s' %
                    (package, profile)
                )


def readme():
    with open('README.rst', 'r') as f:
        return f.read()

setup(
    name='lore',
    version=lore.__version__,
    description='a framework for building and using data science',
    long_description=readme(),
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
    ],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, <4',
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
        'virtualenvwrapper'
    ],
    zip_safe=False,
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
