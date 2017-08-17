from setuptools import setup, find_packages

#with open('README.md') as f:
#    long_description = f.read()
setup(
    name="tetrisRL",
    version="0.4",
    author="Jay Butera",
    author_email="buterajay@gmail.com",
    license="MIT",
    url="https://github.com/jaybutera/tetrisRL",
    packages=find_packages(),
    #long_description=long_description,
    #data_files=[('', ['README'])],
    install_requires=[
        'numpy>=1.13',
        'torch'
    ],
)
