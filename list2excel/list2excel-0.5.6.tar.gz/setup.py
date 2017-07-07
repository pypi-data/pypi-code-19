#!/usr/bin/env python
from list2excel import VERSION

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


bitbucket_url = 'http://bitbucket.org/brente/list2excel/'
long_desc = """
%s

%s
""" % (open('README').read(), open('CHANGELOG').read())

setup(
    name='list2excel',
    version=VERSION,
    description='Django XLS export made easy',
    long_description=long_desc,
    author='Stefano Brentegani',
    author_email='sbrentegani@gmail.com',
    url=bitbucket_url,
    download_url='%sdownloads/list2excel-%s.tar.gz' % (bitbucket_url, VERSION),
    packages=['list2excel'],
    include_package_data=True,
    license='MIT License',
    install_requires=[
        'Django>=1.4,<1.9',
        'xlwt>=0.7.4',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    zip_safe=False,
)
