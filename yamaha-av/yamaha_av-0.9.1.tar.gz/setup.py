from setuptools import setup
setup(
    name="yamaha_av",
    version="0.9.1",
    author="Anthony Casagrande",
    author_email="birdapi@gmail.com",
    description=("Control Yamaha Receivers over the network"),
    license="MIT",
    keywords="yamaha av rxv network receivers birdapi",
    url="https://pypi.python.org/pypi/yamaha_av",
    packages=['yamaha_av'],
    install_requires=[
        "six>=1.10.0,<1.11.0"
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Home Automation",
        "Topic :: System :: Networking",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License"
    ],
)
