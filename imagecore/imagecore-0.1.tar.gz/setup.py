from distutils.core import setup

setup(
    name='imagecore',
    packages=['imagecore'],  # this must be the same as the name above
    version='0.1',
    description='A helper library for parsing Large tifs to feed into ML frameworks',
    author='Mahmoud Lababidi',
    author_email='lababidi@gmail.com',
    url='https://github.com/lababidi/imagecore',  # use the URL to the github repo
    download_url='https://github.com/lababidi/imagecore/archive/0.1.tar.gz',  # I'll explain this in a second
    keywords=['imagery', 'raster', 'machinelearning'],  # arbitrary keywords
    classifiers=[],
    install_requires=['rasterio', 'shapely'],
    python_requires='>=3',
)
