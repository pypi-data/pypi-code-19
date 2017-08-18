#!/usr/bin/python3

from setuptools import setup, find_packages

setup(name = "metallum",
      version = "0.1",
      description = "Console current lyrics visualizer",
      #description_file = "README.rst",

      author = "",
      author_email = "",
      maintainer = "Yeison Cardona",
      maintainer_email = "yeisoneng@gmail.com",

      url = "http://yeisoncardona.com",
      download_url = "",

      license = "GPLv3",
      keywords = "Spotify, lyrics, metallum",

      #classifiers=[#list of classifiers in https://pypi.python.org/pypi?:action=list_classifiers
                   #"Environment :: X11 Applications :: Qt",
                   #"Intended Audience :: Developers",
                   #"License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
                   #"Operating System :: POSIX :: Linux",
                   #"Operating System :: Microsoft :: Windows",
                   #"Operating System :: MacOS",
                   #"Programming Language :: Python",
                   #"Topic :: Software Development",
                   #"Topic :: Software Development :: Code Generators",
                   #"Topic :: Software Development :: Compilers",
                   #"Topic :: Software Development :: Debuggers",
                   #],

      packages = find_packages(),
      include_package_data = True,

      install_requires = [
                          "bs4",
                          "requests",
                          #"gitpython",
                          #"hgapi",
                          #"pyusb==1.0.0b2",
                          #"setuptools",
                          #"wheel"
                          #"pyside",
                          ],
      scripts = [
                 "cmd/metallum",
                 ],

      zip_safe = False,

      )
