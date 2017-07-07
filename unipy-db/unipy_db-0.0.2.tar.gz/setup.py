#-*- coding: utf-8 -*-
"""
Created on 2017-01-05 20:55:26
Modified on 2017-06-26 02:36:25

@author: Young Ju Kim
"""

try:

    from setuptools import setup, find_packages

except ImportError:

    from distutils.core import setup, find_packages


import tarfile


def package_data_listup():

    filename = 'dataset/resources.gz/resources.tar.gz'
    tar = tarfile.open(filename)
    filelist = list(set(map(lambda x: x.split('/')[0], tar.getnames())))
    filelist.sort()
    return filelist


long_desc = """
This is made for some specific environment.
This contains codes for DataBases.
"""

setup(name='unipy_db',
      version='0.0.2',
      description='Useful tools for Data Scientists',
      long_description=long_desc,
      url='http://github.com/pydemia/unipy-db',
      author='Young Ju Kim',
      author_email='pydemia@gmail.com',
      license='MIT License',
      classifiers=[
            # How Mature: 3 - Alpha, 4 - Beta, 5 - Production/Stable
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Programming Language :: Python :: 3.5',
            'Operating System :: OS Independent',
            'Intended Audience :: End Users/Desktop',
            'Intended Audience :: Developers',
            'Intended Audience :: Science/Research',
            'Natural Language :: English',
            ],
      packages=find_packages(exclude=['contrib', 'docs', 'tests']),
      install_requires=[
                        'pandas>=0.20.2',
                        'pymysql',
                        'psycopg2==2.7.1',
                        'sqlalchemy>=1.1.11',
                        'ibm_db_sa>=0.3.3',
                        'cx_Oracle==5.3'
                        ],
      zip_safe=False,
      #package_data={'unipy': ['*.gz', 'dataset/resources.tar.gz']}
      )
