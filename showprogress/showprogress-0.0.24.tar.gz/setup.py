from description import __version__, __author__
from setuptools import setup, find_packages

setup(
   name="showprogress",
   version=__version__,
   author=__author__,
   author_email='soy.lovit@gmail.com',
   url='https://github.com/lovit/showprogress',
   description="Simple utils",
   long_description="""Simple utils""",
   install_requires=["psutil>=5.0.1"],
   keywords = ['progress'],
   packages=find_packages(),
)