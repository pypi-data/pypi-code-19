from distutils.core import setup

PACKAGE = "ECO_NLP_VERS"
NAME = "ECO_NLP_VERS"
DESCRIPTION = "This package provides tools for analyzing the influence of economic news on Chinese stock market."
AUTHOR = "VersElectronics"
AUTHOR_EMAIL = "jiachengzhu1994@gmail.com"

setup(
    name=NAME,
    version="0.0.1",
    description=DESCRIPTION,
    # long_description=read("README.md"),
    author=AUTHOR,
    url= "https://github.com/VersElectronics/ECO_NLP_VERS",
    author_email=AUTHOR_EMAIL,
    license="MIT Licences",

    packages=["ECO_NLP_VERS"],
    install_requires=[
        "jieba",
        "SnowNLP"
        ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.5",
    ],
    zip_safe=False,
)