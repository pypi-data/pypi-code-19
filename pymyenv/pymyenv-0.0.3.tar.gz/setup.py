import setuptools

import sys
if not sys.version_info[0] == 3:
    sys.exit("Sorry, only python version 3 is supported")

setuptools.setup(
    name='pymyenv',
    version='0.0.3',
    description='pymyenv is a module to help you switch virtualenv easily',
    long_description='pymyenv is a module to help you switch virtualenv easily',
    url='https://veltzer.github.io/pymyenv',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    keywords='python virtualenv pip',
    packages=setuptools.find_packages(),
    install_requires=[
        'click',  # for command line parsing
        'pyfakeuse'  # for fake use of variables
    ],
    entry_points={
        'console_scripts': [
            # 'pymyenv_foo=pymyenv.scripts.foo:main',
        ],
    },
)
