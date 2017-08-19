from setuptools import setup
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='s1acker',
    use_scm_version=True,
    description='Search and download images from stage1st',
    long_description=long_description,
    url='https://github.com/quinoa42/s1acker',
    author='quinoa42',
    author_email='',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3 :: Only'
    ],
    keywords='crawler stage1st',
    packages=['s1acker'],
    install_requires=[
        'beautifulsoup4==4.6.0', 'lxml==3.8.0', 'requests==2.18.3'
    ],
    python_requires='>=3.6, <4',
    setup_requires=['setuptools_scm'],
    include_package_data=True,
    entry_points={'console_scripts': ['s1acker=s1acker.cli:main']}
)
