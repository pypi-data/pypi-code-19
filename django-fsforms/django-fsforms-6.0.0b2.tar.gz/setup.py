#!/usr/bin/env python3
import os
import re
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


def get_version(*file_paths):
    """Retrieves the version from the given file path."""
    filename = os.path.join(os.path.dirname(__file__), *file_paths)
    version_file = open(filename).read()
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


try:
    import pypandoc
    readme = pypandoc.convert('README.md', 'rst')
    changelog = pypandoc.convert('CHANGELOG.md', 'rst')
except ImportError:
    if 'sdist' in sys.argv or 'bdist_wheel' in sys.argv:
        raise RuntimeError("You must install 'pypandoc' at first.")
    print("Warning! You will have to install 'pypandoc' if you want to "
          "build the package and upload it on PyPi.")
    readme = open('README.md').read()
    changelog = open('CHANGELOG.md').read()

version = get_version('fsforms', '__init__.py')

setup(
    name='django-fsforms',
    version=version,
    description=(
        "A reusable Django application for rendering forms with "
        "Foundation for Sites."
    ),
    long_description=readme + '\n\n' + changelog,
    author='Jérôme Lebleu',
    author_email='jerome.lebleu@cliss21.org',
    url='https://forge.cliss21.org/cliss21/django-fsforms',
    packages=[
        'fsforms',
    ],
    include_package_data=True,
    install_requires=[],
    license="GNU AGPL-3",
    zip_safe=False,
    keywords='django-fsforms',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
)
