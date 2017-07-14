from setuptools import setup, find_packages
from ORCSchlange import __version__
import os.path


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="ORCSchlange",
    version=__version__,
    packages=find_packages(),
    package_data={"ORCSchlange.command": "*.js"},
    zip_safe=False,
    install_requires=['pybtex>=0.21', 'requests>=2.18.1'],
    author="Fabian Gaertner",
    author_email="fabian@bioinf.uni-leipzig.de",
    url="https://github.com/ScaDS/ORC-Schlange",
    description="Create a nice static publishing websites from ORCIDs.",
    license="Apache 2.0",
    long_description=read('docs/README.rst'),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6"
    ],
    entry_points={
        'console_scripts': [
            'orcs = ORCSchlange.__main__:main'
        ]
    },
    command_options={
        'build_sphinx': {
            'version': ('setup.py', __version__),
            'release': ('setup.py', __version__)
        }
    },
    keywords="ORCID Website Bibliography Publication ScaDS"
)
