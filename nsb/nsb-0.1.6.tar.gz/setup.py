from setuptools import setup
setup(
    name = 'nsb',
    packages = ['nsb', 'nsb/gaia', 'nsb/mypycat'],
    version = '0.1.6',
    description = 'Draws nightsky allskymaps',
    long_description = 'Draws nightsky allskymaps corresponding to KRISCIUNAS Model of the Brightness of Moonlight, '
                'together with star data obtained from the GAIA public data release catalog. '
                'The result is a 2D Pixel array with physical brightness values for each sky position.',
    author='Matthias Buechele',
    author_email='matthias.buechele@fau.de',
    url='https://git.ecap.work/mbuechele/allskymaps',
    download_url='https://git.ecap.work/mbuechele/allskymaps/repository/archive.tar?ref=0.0.2',
    install_requires=['healpy','tqdm', 'ephem', 'astropy', 'scipy', 'numpy', 'matplotlib'],
    package_dir={'nsb': 'nsb'},
    package_data={'nsb': ['gaia/ducaticat.txt']},
    entry_points = {
        "console_scripts": ['nsb = nsb.nsb:main']
        },
)
# package_data={'nsb': ['gaia/ducaticat.txt','mypycat/cat.csv', 'config.cfg']},