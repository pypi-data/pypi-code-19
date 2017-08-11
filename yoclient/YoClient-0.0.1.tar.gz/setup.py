from setuptools import setup, find_packages
setup(
  name="YoClient",
  packages=find_packages(exclude=["tests*"]),
  install_requires=["requests"],
  version="0.0.1",
  description="Yo Client",
  author="Jae Bradley",
  author_email="jae.b.bradley@gmail.com",
  url="https://github.com/jaebradley/yo_client",
  download_url="https://github.com/jaebradley/yo_client/tarball/0.1",
  keywords=["yo"],
  classifiers=[],
)
