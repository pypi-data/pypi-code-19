from setuptools import setup

setup(
    name="birdparse",
    version="0.1.1",
    author="Anthony Casagrande",
    author_email="birdapi@gmail.com",
    description=("Generic object parser for python supporting yaml and json"),
    license="MIT",
    keywords="yaml json birdapi",
    url="https://pypi.python.org/pypi/birdparse",
    packages=['birdparse'],
    install_requires=[
        "birdyaml>=0.1.0<=0.2.0",
        "birdjson>=0.9.1<=1.0.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
    ],
)
