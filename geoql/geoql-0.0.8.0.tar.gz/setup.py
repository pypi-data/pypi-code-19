from setuptools import setup

setup(
    name             = 'geoql',
    version          = '0.0.8.0',
    packages         = ['geoql',],
    install_requires = ['geojson', 'geopy', 'rtree', 'shapely', 'tqdm',],
    license          = 'MIT',
	url              = 'https://github.com/Data-Mechanics/geoql',
	author           = 'Andrei Lapets',
	author_email     = 'a@lapets.io',
    description      = 'Library for performing queries and transformations on GeoJSON data (with emphasis on support for abstract graph representations).',
    long_description = open('README.rst').read(),
)
