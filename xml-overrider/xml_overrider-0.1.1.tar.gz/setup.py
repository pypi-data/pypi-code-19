import os

from setuptools import find_packages, setup

from xml_overrider import __version__


def read(*parts):
    """Read contents of a file relative to the package root."""
    path = os.path.abspath(os.path.join(os.path.dirname(__file__), *parts))
    content = ""

    with open(path) as fp:
        content = fp.read()

    return content


setup(
    name="xml_overrider",
    version=__version__,
    author="Victor Pantoja",
    author_email="victor.pantoja@gmail.com",
    description="Simple way to override XML values based on based on xpaths",
    long_description='\n\n'.join([
        read('README.md'),
        read('CHANGELOG.rst'),
    ]),
    url='https://github.com/victorpantoja/xml_overrider',
    keywords=["accounts"],
    license="Proprietary License",
    platforms=["Linux"],
    zip_safe=False,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'lxml==3.8.0',
        'pyyaml==3.12',
        'docopt == 0.6.2',
    ],
    dependency_links=[

    ],
    entry_points={
        'console_scripts': [
            'xml-overrider = xml_overrider.overrider:overrider'
        ]
    },
)
