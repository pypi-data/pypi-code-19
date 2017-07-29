import setuptools

import sys
if not sys.version_info[0] == 3:
    sys.exit("Sorry, only python version 3 is supported")

setuptools.setup(
    name='pypathutil',
    version='0.0.10',
    description='pypathutil is a module to help you deal with paths',
    long_description='pypathutil is a module to help you deal with paths',
    url='https://veltzer.github.io/pypathutil',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    keywords='python path utils bash',
    packages=setuptools.find_packages(),
    install_requires=[
        'click',  # for command line parsing
        'pyfakeuse'  # for fake use of variables
    ],
    entry_points={
        'console_scripts': [
            'pypathutil_add=pypathutil.scripts.add:main',
            'pypathutil_clean=pypathutil.scripts.clean:main',
            'pypathutil_remove=pypathutil.scripts.remove:main',
        ],
    },
)
