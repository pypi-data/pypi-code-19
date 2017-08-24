# coding=utf-8
"""Setup file for distutils / pypi."""
try:
    from ez_setup import use_setuptools
    use_setuptools()
except ImportError:
    pass

from setuptools import setup, find_packages


setup(
    name='inasafe-cli',
    version='1.0.0',
    packages=find_packages(),
    license='GPL',
    author='InaSAFE Team',
    author_email='info@inasafe.org',
    url='http://inasafe.org/',
    description=('Realistic natural hazard impact scenarios for better '
                 'planning, preparedness and response activities.'),
    install_requires=[
        'inasafe-core',
        'docopt'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Scientific/Engineering :: GIS',
    ],
)
