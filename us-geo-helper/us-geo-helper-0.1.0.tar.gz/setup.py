from setuptools import setup
exec(open('us-geo-helper/version.py').read())
setup(
    name = 'us-geo-helper',
    packages = ['us-geo-helper'], # this must be the same as the name above
    version = __version__,
    description = 'Python wrapper for US Census Data',
    author = 'Philip Sun',
    author_email = 'traders@mit.edu',
    license = 'MIT',
    url = 'https://github.com/sammymax/us-geo-helper',
    download_url = 'https://github.com/sammymax/us-geo-helper/tarball/' + __version__,
    install_requires = ['numpy', 'pandas'],
    keywords = ['geography'],
    classifiers = [
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)
