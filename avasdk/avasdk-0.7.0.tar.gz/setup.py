from setuptools import setup, find_packages

import avasdk

keywords = [
    'ava', 'sdk',
]

setup(
    name='avasdk',
    version=avasdk.__version__,
    description=avasdk.__doc__,
    author=avasdk.__author__,
    license='Apache',
    url=avasdk.__url__,
    keywords=keywords,
    packages=find_packages(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
    install_requires=['valideer'],
)
