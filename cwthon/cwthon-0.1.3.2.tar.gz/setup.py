from setuptools import setup, find_packages

setup(
    name='cwthon',
    description="A Python wrapper of KDDI's ChatWork API",
    version='0.1.3.2',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    author='ginyolith',
    url='https://github.com/ginyolith/cwthon',
    author_email='ginolith@gmail.com',
    keywords='chatwork api wrapper',
    install_requires=['requests'],
)
