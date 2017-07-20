from setuptools import setup
import nsb.__main__ as main
setup(
    name = 'nsb',
    packages = ['nsb', 'nsb/gaia', 'nsb/mypycat'],
    version = main.__version__,
    description = main.__description__,
    long_description = main.__long_description__,
    author= main.__author__,
    author_email= main.__author_email__,
    url='https://pypi.python.org/pypi/nsb',
    install_requires=['healpy','tqdm', 'ephem', 'astropy', 'scipy', 'numpy', 'matplotlib'],
    package_dir={'nsb': 'nsb'},
    package_data={'nsb': ['gaia/ducaticat.txt']},
    entry_points = {
        "console_scripts": ['nsb = nsb.nsb:main']
        },
    classifiers=[
              'Development Status :: 3 - Alpha',
              'Environment :: Console',
              'Intended Audience :: Science/Research',
              'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
              'Operating System :: POSIX :: Linux',
              'Topic :: Scientific/Engineering :: Astronomy',
              'Topic :: Scientific/Engineering :: Atmospheric Science',
              'Topic :: Scientific/Engineering :: Physics',
              ],
)
# package_data={'nsb': ['gaia/ducaticat.txt','mypycat/cat.csv', 'config.cfg']},