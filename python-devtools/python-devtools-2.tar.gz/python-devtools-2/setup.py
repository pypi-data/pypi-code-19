from pathlib import Path
from setuptools import setup

THIS_DIR = Path(__file__).resolve().parent
long_description = THIS_DIR.joinpath('README.rst').read_text()

setup(
    name='python-devtools',
    version='2',
    description='Dev tools for python',
    long_description=long_description,
    author='Samuel Colvin',
    author_email='s@muelcolvin.com',
    url='https://github.com/samuelcolvin/python-devtools',
    license='MIT',
    packages=[],
    python_requires='>=3.5',
    zip_safe=True,
)
