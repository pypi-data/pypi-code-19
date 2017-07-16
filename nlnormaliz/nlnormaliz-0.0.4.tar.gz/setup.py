import re
import setuptools


setuptools.setup(
    name="nlnormaliz",
    version=re.search(r"__version__ *= *'([0-9]+\.[0-9]+\.[0-9]+)' *\n",
                      open("nlnormaliz/__init__.py").read()).group(1),
    description="Natural language normalizer for documents in Python",
    long_description=open("README.md").read(),
    license="Public Domain",
    author="Yota Toyama",
    author_email="raviqqe@gmail.com",
    url="https://github.com/raviqqe/nlnormaliz.py/",
    packages=["nlnormaliz"],
    entry_points={
            "console_scripts": ["nlnormaliz=nlnormaliz.__main__:main"]
    },
    install_requires=["iso639", "langdetect", "neologdn"],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: Public Domain",
        "Natural Language :: English",
        "Natural Language :: Japanese",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Text Processing :: Linguistic",
    ],
)
