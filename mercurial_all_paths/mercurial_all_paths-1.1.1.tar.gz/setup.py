
VERSION = '1.1.1'

#pylint:disable=missing-docstring,unused-import,import-error

try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

LONG_DESCRIPTION = open("README.txt").read()

setup(
    name="mercurial_all_paths",
    version=VERSION,
    author='Marcin Kasperski',
    author_email='Marcin.Kasperski@mekk.waw.pl',
    url='http://bitbucket.org/Mekk/mercurial-all_paths',
    description='Mercurial allpaths extension',
    long_description=LONG_DESCRIPTION,
    license='GNU General Public License v2 (GPLv2)',
    py_modules=[
        'mercurial_all_paths',
    ],
    install_requires=[
        'mercurial_extension_utils>=1.2.0',
    ],
    keywords="mercurial paths multi extension",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: DFSG approved',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Version Control'
        #'Topic :: Software Development :: Version Control :: Mercurial',
    ],
    zip_safe=True)
