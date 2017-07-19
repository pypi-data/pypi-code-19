from distutils.core import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README')) as f:
    long_description = f.read()

setup(
    name ='eyeon',
    version ='0.1.3',
    description ='Simple CLI tool to watch html and css files and reload the browser on change.',
    long_description = long_description,
    author ='John Morrison',
    author_email ='john@johmorrison.io',
    url = "https://github.com/jgmorrison/eyeOn-py",
    packages = ["eyeon"],
    entry_points = {"console_scripts" : ["eyeon = eyeon.__main__:main"]}
)
