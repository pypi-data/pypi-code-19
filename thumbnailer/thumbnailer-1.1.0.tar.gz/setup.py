#!/usr/bin/env python3
"Setup script"

from distutils.core import setup

with open("README.rst") as f:
    LNG_DSC = f.read()

setup(
    name="thumbnailer",
    version="1.1.0",
    description="Module to turn images into thumbnails.",
    long_description=LNG_DSC,
    author="Sönke Lambert",
    author_email="soelam@live.de",
    url="https://github.com/ekkkkkknoes/thumbnailer",
    license="BSD-2-Clause",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "License :: OSI Approved :: BSD License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Multimedia :: Graphics :: Graphics Conversion"
    ],
    keywords="images tools",
    install_requires=["Pillow"],
    python_requires=">=3",
    packages=["thumbnailer"],
    entry_points={
        "console_scripts": [
            'thumbnailer=thumbnailer:main',
        ],
    }
)
