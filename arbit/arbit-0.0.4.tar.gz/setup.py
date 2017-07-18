from setuptools import setup, find_packages

setup(
    name="arbit",
    version="0.0.4",
    author='Tjaden Hess',
    author_email='tjaden@1protocol.com',

url="https://github.com/1protocol/arbit-pypi",
    license='GPL3',
    description='Native Arbit client',
    setup_requires=["cffi>=1.0.0"],
    cffi_modules=["arbit/arbit_build.py:ffibuilder"],
    install_requires=["cffi>=1.0.0"],
    packages=["arbit"],
    entry_points = {
        'console_scripts': ['arbit=arbit:main'],
    }
)
