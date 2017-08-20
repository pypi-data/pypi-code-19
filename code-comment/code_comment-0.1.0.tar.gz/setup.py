# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


VERSION = '0.1.0'
REPO_URL = 'https://github.com/kelvintaywl/code_comment'

requires = []

extras_require = {
    "test": [
        "pytest",
        "pytest-cov",
        "flake8"
    ]
}

classifiers = [
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6'
]

setup(name='code_comment',
      version=VERSION,
      description='extracts code comments from source codes',
      author='Kelvin Tay',
      author_email='kelvintay@gmail.com',
      url=REPO_URL,
      license='MIT',
      classifiers=classifiers,
      download_url='{}/tarball/{}'.format(REPO_URL, VERSION),
      keywords='comment, extract',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      extras_require=extras_require)
