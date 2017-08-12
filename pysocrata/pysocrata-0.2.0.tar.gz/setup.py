from setuptools import setup
setup(
    name = 'pysocrata',
    packages = ['pysocrata'], # this must be the same as the name above
    install_requires=['pandas', 'requests'],
    py_modules=['pysocrata'],
    version = '0.2.0',
    description = 'Python module for interfacing with Socrata open data platform metadata.',
    author = 'Aleksey Bilogur',
    author_email = 'aleksey.bilogur@gmail.com',
    url = 'https://github.com/ResidentMario/pysocrata',
    download_url = 'https://github.com/ResidentMario/pysocrata/tarball/0.2.0',
    keywords = ['data', 'socrata', 'open data'],
    classifiers = [],
)