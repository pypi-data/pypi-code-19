from setuptools import setup, find_packages

try:
    with open('README.rst') as f:
        readme = f.read()
except IOError:
    readme = ''

setup(
    name="tornado-whois",
    version="0.7",
    keywords=["tornado", "whois", "tornado-whois", "asyncwhois"],
    description="Asynchronous python tornado whois client",
    long_description=readme,
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
    ],
    install_requires=["tornado>=4.3"],
    requires=["tornado (>=4.3)"],
)
