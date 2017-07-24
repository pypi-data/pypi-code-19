from setuptools import setup, find_packages
from multiscale import __version__

with open("readme.md") as f:
  long_description = f.read()

setup(
  name="multiscale",
  version=__version__,
  packages=find_packages(),

  install_requires=["docopt", "PythonMagick"],

  author="Attila V. Molnar",
  author_email="ate.molnar2@gmail.com",
  description="Scale images from input directories to multiple resolution levels separated into multiple directories",
  long_description=long_description,
  classifiers=[
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.4",
        "Topic :: Multimedia :: Graphics",
    ],
  license="MIT",
  keywords="scale image image-manipulation PythonMagick",
  url="https://github.com/AttilaVM/multiscale"
)
