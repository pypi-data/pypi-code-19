from setuptools import setup

setup(
    name="birdyaml",
    version="0.1.0",
    author="Anthony Casagrande",
    author_email="birdapi@gmail.com",
    description=("Generic yaml to object parser for python"),
    license="MIT",
    keywords="yaml birdapi",
    url="https://pypi.python.org/pypi/birdyaml",
    packages=['birdyaml'],
    install_requires=[
        "PyYAML==3.12"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)