from distutils.core import setup
from setuptools import find_packages

required = [
    "pandas>=0.15.2",
    "geopandas>=0.2",
    "shapely>=1.5.13",
    "memoized-property>=1.0.0",
    "python-geohash>=0.8.5"
]

setup(
    name="polygeohash",
    version="0.1",
    author="Mathieu Ripert",
    author_email="mathieu@instacart.com",
    url="https://github.com/mathieuripert/polygeohash",
    license="MIT",
    packages=find_packages(),
    package_dir={"polygeohash": "polygeohash"},
    description="Transform a geoJSON into a list of geohashes that intersect with it",
    install_requires=required,
    classifiers=[
        # Maturity
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',
        # Versions supported
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],

)
