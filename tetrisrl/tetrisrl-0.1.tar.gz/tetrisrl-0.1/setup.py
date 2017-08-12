from setuptools import setup, find_packages
setup(
    name="tetrisrl",
    version="0.1",
    author="Jay Butera",
    author_email="buterajay@gmail.com",
    url="https://github.com/jaybutera/tetrisRL",
    packages=find_packages(),
    install_requires=[
        'numpy>=1.13'
    ],
)
