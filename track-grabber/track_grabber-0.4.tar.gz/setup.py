from setuptools import setup

setup(name="track_grabber",
      version="0.4",
      description="Track grabber finds the most popular songs of a given artists and generates an html page with youtube links to those songs.",
      author="Joseph Jones",
      py_modules=["track_grabber"],
      install_requires=["requests", "BeautifulSoup4", "tqdm"]
     )
