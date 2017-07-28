import os
from setuptools import setup

try:
    import pypandoc

    README = pypandoc.convert_file('README.md', 'rst')
except ImportError:
    with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
        README = readme.read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='levit-report',
    version='0.9.12',
    packages=['levit_report', 'levit_report.migrations'],
    include_package_data=True,
    license='MIT License',  # example license
    description='Package description',
    long_description=README,
    url='http://levit.be',
    author='LevIT scs',
    author_email='foss@levit.be',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['Django>=1.8', 'relatorio>=0.6.1', ]
)
