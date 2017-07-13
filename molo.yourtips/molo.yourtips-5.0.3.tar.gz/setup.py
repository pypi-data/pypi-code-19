import os

from setuptools import setup, find_packages

description_files = ["README.rst", "AUTHORS.rst", "CHANGES.rst"]

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'requirements.txt')) as f:
    requires = filter(None, f.readlines())

with open(os.path.join(here, 'requirements-dev.txt')) as f:
    requires_dev = filter(None, f.readlines())

with open(os.path.join(here, 'VERSION')) as f:
    version = f.read().strip()

setup(name='molo.yourtips',
      version=version,
      description=('This feature enables youth to share short tips with one '
                   'another'),
      long_description="".join([open(f, "r").read() for f in description_files]),
      classifiers=[
          "Programming Language :: Python",
          "Framework :: Django",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
      ],
      author='Praekelt Foundation',
      author_email='dev@praekelt.com',
      url='https://github.com/praekeltfoundation/molo.yourtips',
      license='BSD',
      keywords='praekelt, mobi, web, django',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      namespace_packages=['molo'],
      install_requires=requires,
      tests_require=requires_dev,
      entry_points={})
