#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Andre Anjos <andre.anjos@idiap.ch>
# Mon 16 Apr 08:18:08 2012 CEST
#

from setuptools import setup, dist

dist.Distribution(dict(setup_requires=['bob.extension']))

from bob.extension.utils import load_requirements, find_packages

install_requires = load_requirements()

# The only thing we do in this file is to call the setup() function with all
# parameters that define our package.
setup(

    # This is the basic information about your project. Modify all this
    # information before releasing code publicly.
    name='bob.paper.interspeech_2016',
    version=open("version.txt").read().rstrip(),
    description='Cross-database evaluation of audio-based spoofing detection systems',

    url='https://gitlab.idiap.ch/bob/bob.paper.interspeech_2016',
    license='BSD',
    author='Pavel Korshunov',
    author_email='pavel.korshunov@idiap.ch',
    keywords="PAD experiments, paper package, cross-database testing",

    # If you have a better, long description of your package, place it on the
    # 'doc' directory and then hook it here
    long_description=open('README.rst').read(),

    # This line is required for any distutils based packaging.
    packages=find_packages(),
    include_package_data=True,

    install_requires=install_requires,


    entry_points={
        'console_scripts': [
            'pad_process_scores.py         = bob.paper.interspeech_2016.scripts.pad_process_scores:main',
            'pad_stats_summary.py         = bob.paper.interspeech_2016.scripts.pad_stats_summary:main',
            'pad_diff_sys_scores.py         = bob.paper.interspeech_2016.scripts.pad_diff_sys_scores:main',
        ],
    },

    classifiers=[
        'Framework :: Bob',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Database :: Front-Ends',
    ],
)
