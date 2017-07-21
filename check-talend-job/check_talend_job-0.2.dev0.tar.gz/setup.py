# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os


version = '0.2-dev'

here = os.path.abspath(os.path.dirname(__file__))

def read_file(*pathes):
    path = os.path.join(here, *pathes)
    if os.path.isfile(path):
        with open(path, 'r') as desc_file:
            return desc_file.read()
    else:
        return ''

desc_files = (('README.md',), ('docs', 'CHANGES.rst'),
                ('docs', 'CONTRIBUTORS.rst'))

long_description = '\n\n'.join([read_file(*pathes) for pathes in desc_files])

install_requires=['setuptools']


setup(name='check_talend_job',
      version=version,
      description="A nagios-like plugin to check if talend jobs executed successfully",
      long_description=long_description,
      platforms = ["any"],
      # Get more strings from
      # http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        ],
      keywords="nagios",
      author="Elio Maisonneuve",
      author_email="maisonneuv@eisti.eu",
      url="https://github.com/paulla/check_talend_job",
      license="BSD",
      packages=find_packages("src"),
      package_dir = {"": "src"},
      include_package_data=True,
      zip_safe=False,
      install_requires=install_requires,
      entry_points="""
      # -*- Entry points: -*-
      [console_scripts]
      check_talend_job = check_talend_job:main
      """,
      )

# vim:set et sts=4 ts=4 tw=80:
