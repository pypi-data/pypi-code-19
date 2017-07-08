import os
import re
from setuptools import setup, find_packages


def docs_read(fname):
    return open(os.path.join(os.path.dirname(__file__), 'docs', fname)).read()


def version_read():
    settings_file = open(os.path.join(os.path.dirname(__file__), 'lib', 'ufodiff', 'settings.py')).read()
    major_regex = """major_version\s*?=\s*?["']{1}(\d+)["']{1}"""
    minor_regex = """minor_version\s*?=\s*?["']{1}(\d+)["']{1}"""
    patch_regex = """patch_version\s*?=\s*?["']{1}(\d+)["']{1}"""
    major_match = re.search(major_regex, settings_file)
    minor_match = re.search(minor_regex, settings_file)
    patch_match = re.search(patch_regex, settings_file)
    major_version = major_match.group(1)
    minor_version = minor_match.group(1)
    patch_version = patch_match.group(1)
    if len(major_version) == 0:
        major_version = 0
    if len(minor_version) == 0:
        minor_version = 0
    if len(patch_version) == 0:
        patch_version = 0
    return major_version + "." + minor_version + "." + patch_version


setup(
    name='ufodiff',
    version=version_read(),
    description='UFO font source file diff tool',
    long_description=(docs_read('README.rst')),
    url='https://github.com/source-foundry/ufodiff',
    license='MIT license',
    author='Christopher Simpkins',
    author_email='chris@sourcefoundry.org',
    platforms=['any'],
    packages=find_packages("lib"),
    package_dir={'': 'lib'},
    install_requires=['commandlines', 'standardstreams', 'gitpython'],
    entry_points={
        'console_scripts': [
            'ufodiff = ufodiff.app:main'
        ],
},
    keywords='font, typeface, ufo, diff, source, ttf, otf',
    include_package_data=True,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
