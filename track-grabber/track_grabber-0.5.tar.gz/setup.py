from setuptools import setup

setup(name="track_grabber",
      version="0.5",
      description="Track grabber finds the most popular songs of a given artists and generates an html page with youtube links to those songs.",
      author="Joseph Jones",
      author_email="josephjones15470@gmail.com",
      url="https://pypi.python.org/pypi/track-grabber",
      py_modules=["track_grabber"],
      install_requires=["requests", "BeautifulSoup4", "tqdm"]
     )
