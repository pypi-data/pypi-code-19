from bgparsers import __version__
from setuptools import setup, find_packages

setup(
    name='bgparsers',
    version=__version__,
    packages=find_packages(),
    author='BBGLab (Barcelona Biomedical Genomics Lab)',
    author_email='bbglab@irbbarcelona.org',
    description="Bgconfig library to manage configuration files.",
    license="Apache License 2",
    keywords="",
    url="https://bitbucket.org/bgframework/bgconfig",
    download_url="https://bitbucket.org/bgframework/bgconfig/get/"+__version__+".tar.gz",
    install_requires=[
        "tqdm",
        "bgconfig",
        "itab",
        "click",
        "numpy",
        "intervaltree"
    ],
    entry_points={
            'console_scripts': [
                'bgvariants = bgparsers.commands.bgvariants:cli',
            ]
        }
)