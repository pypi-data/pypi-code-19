from setuptools import setup, find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = 0.1

setup(
    name='pyhnalgolia',
    version=version,
    install_requires=requirements,
    author='delusionX',
    author_email='babinec.peter@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/xbabinec/pyhnalgolia/',
    license='MIT',
    description='Unofficial Python wrapper for https://hn.algolia.com/api',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
