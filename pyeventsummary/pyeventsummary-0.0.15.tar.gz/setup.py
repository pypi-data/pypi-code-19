import setuptools

import sys
if not sys.version_info[0] == 3:
    sys.exit("Sorry, only python version 3 is supported")

setuptools.setup(
    name='pyeventsummary',
    version='0.0.15',
    description='pyeventsummary is a way to aggregate and report on a host of errors and actions',
    long_description='pyeventsummary is a way to aggregate and report on a host of errors and actions',
    url='https://veltzer.github.io/pyeventsummary',
    author='Mark Veltzer',
    author_email='mark.veltzer@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
    ],
    keywords='python summary errors actions aggregate print enum',
    packages=setuptools.find_packages(),
)
