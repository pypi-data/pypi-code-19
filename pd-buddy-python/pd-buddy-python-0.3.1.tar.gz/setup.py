from setuptools import setup

with open("README.rst") as file:
    long_description = file.read()

setup(
    name = "pd-buddy-python",
    version = "0.3.1",
    author = "Clayton G. Hobbs",
    author_email = "clay@lakeserv.net",
    description = ("Python library for configuring PD Buddy Sink devices"),
    license = "GPLv3+",
    keywords = "usb serial pd-buddy configuration",
    url = "https://git.clayhobbs.com/pd-buddy/pd-buddy-python",
    packages = ['pdbuddy'],
    long_description = long_description,
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 or later "
            "(GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: User Interfaces"
    ],
    install_requires=[
        "pyserial>=3,<4",
        "aenum>=2;python_version<'3.6'"
    ],
    test_suite="test_pdbuddy"
)
