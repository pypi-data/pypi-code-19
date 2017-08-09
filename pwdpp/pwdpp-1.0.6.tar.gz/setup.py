import sys
from setuptools import setup


def get_long_description():
    descr = []
    for fname in ('README.rst',):
        with open(fname) as f:
            descr.append(f.read())
    return '\n\n'.join(descr)


setup(
    name="pwdpp",
    py_modules=['pwdpp'],
    entry_points={
        'console_scripts': [
            'pwdpp = pwdpp:main',
            ],
        },
    install_requires={
        'psutil': ["psutil"],
        } if sys.platform == "win32" else {},

    zip_safe=False,
    version="1.0.6",

    description='Portable pwd (print working directory).',
    long_description=get_long_description(),
    license="BSD 3-Clause License",
    keywords="pwd, portable, windows, cygwin, msys, msys2",
    url="https://bitbucket.org/hhsprings/pwdpp",
    author="Hiroaki Itoh",
    author_email="xwhhsprings@gmail.com",
    classifiers=[
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: BSD License",
        "Environment :: Console",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        ],
    )
