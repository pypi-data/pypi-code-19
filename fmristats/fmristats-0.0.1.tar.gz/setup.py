from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='fmristats',
    version='0.0.1',
    description='Rigorous statistical modelling of functional MRI data',
    long_description=long_description,
    url='https://github.com/00tau/fmristats/',
    author='Thomas W. D. Möbius',
    author_email='moebius@medinfo.uni-kiel.de',
    license='GPLv3+',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='fmri statistics meta-analysis meta-regression imaging neuroimaging',
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=['numpy', 'scipy', 'scikit-image',
        'pandas', 'statsmodels', 'nibabel',
        'matplotlib', 'seaborn'],
#    entry_points={
#        'console_scripts': [
#            'fmrisetup = fmristats.tools.fmrisetup:fmrisetup_command',
#            'fmrisummary = fmristats.tools.fmrisummary:fmrisummary_command',
#            'fmrianalysis = fmristats.tools.fmrianalysis:fmrianalysis_command',
#            'fmriassessment = fmristats.tools.fmriassessment:fmriassesment_command',
#            'fmrireplace = fmristats.tools.fmrireplace:fmrireplace_command',
#            'fmrirun = fmristats.tools.fmrirun:fmrirun_command',
#            'mat2irritation = fmristats.tools.mat2irritation:mat2irr_command',
#            'fsl2diffeo = fmristats.tools.fsl2diffeo:fsl2diffeo_command',
#        ],
#    },
#    scripts = [
#            'bin/...',
#            ]
)
