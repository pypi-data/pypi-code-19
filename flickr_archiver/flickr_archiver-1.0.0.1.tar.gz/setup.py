from setuptools import setup
import os

desc = open("readme.rst").read() if os.path.isfile("readme.rst") else ""


setup(
    name='flickr_archiver',
    version='1.0.0.1',
    packages=['flickr_archiver'],
    url='https://github.com/tahoe/flickr_archiver/',
    download_url='https://github.com/tahoe/flickr_archiver/tarball/1.0.0.1',
    license='MIT',
    long_description=desc,
    keywords='fun shit',
    author='Dennis Durling',
    author_email='djdtahoe@gmail.com',
    description='Does what it says it does',
    zip_safe=False,
    include_package_data=True,
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        'flickr-api==0.5',
        'PyYAML==3.12',
        'Faker==0.7.12',
    ],
    entry_points={
        'console_scripts': [
            'flickrarchiver=flickr_archiver:main',
        ],
    },
)

