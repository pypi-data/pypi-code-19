import os
from setuptools import setup
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()
packages = ["easyGrad"]
setup(
    name = "easyGrad",
    version = "0.0.2",
    author = "Amartya Sanyal",
    author_email = "amartya18x@gmail.com",
    description = ("A python package to do auto differentiation."),
    license = "BSD",
    keywords = "autodiff machine-learning deep learning",
    url = "http://packages.python.org/easyGrad",
    packages = packages,
    long_description=read('README.md'),
    dependency_links = [],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['numpy']
)
