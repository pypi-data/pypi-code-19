# Copyright (c) 2017 Peter Tonner
#
# GNU GENERAL PUBLIC LICENSE
#    Version 3, 29 June 2007
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from setuptools import setup, find_packages, Extension
from setuptools.command.install import install

from os import path

here = path.abspath(path.dirname(__file__))
# Get the long description from the README file
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


class CustomInstall(install):

    def run(self):
        install.run(self)

        self.buildModels()

    def buildModels(self):
        from pystan import StanModel

        for mf in ['noncentered']:
            m = StanModel('phenom/models/%s.stan' % mf)
            with open('phenom/models/%s.pkl' % mf, 'wb') as f:
                pickle.dump(m, f)

use_cython = False
try:
    from Cython.Distutils import build_ext
    from Cython.Build import cythonize
except ImportError:
    use_cython = False

cmdclass = {'install': CustomInstall}
ext_modules = []

if use_cython:
    ext_modules += cythonize(["phenom/*.pyx"])
    cmdclass.update({'build_ext': build_ext})
else:
    ext_modules += [
    ]


setup(
    name='phenom',

    cmdclass=cmdclass,
    ext_modules=ext_modules,

    version='0.0.1.1a',
    description='population growth phenotype model',
    long_description=long_description,
    author='Peter Tonner',
    author_email='peter.tonner@duke.edu',

    license='GPLv3',

    packages=find_packages(),
    url='https://gitlab.oit.duke.edu/pt59/phenom',

    keywords='bayesian statistics time-course',

    install_requires=[
        'scipy>=0.17.1',
        'numpy>=1.11.0',
        'pandas>=0.18.1',
        'matplotlib>=1.5.1',
        'pystan'
    ],

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering',
        'Programming Language :: Python',
    ],

    entry_points={
        'console_scripts': [
            'phenom=phenom.__main__:main',
        ],
    },

)
