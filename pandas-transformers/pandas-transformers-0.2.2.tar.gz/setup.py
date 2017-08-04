from setuptools import setup, find_packages

from pip.req import parse_requirements

install_reqs = parse_requirements('requirements.txt', session='hack')
req = [str(ir.req) for ir in install_reqs]
setup(
    name='pandas-transformers',
    version='0.2.2',
    author="Oguzhan Sagoglu",
    author_email="alwaysprep@gmail.com",
    description="Use pandas dataframes in sklearn pipelines",
    license="MIT",
    keywords="pandas sklearn pipeline transformers",
    packages=find_packages(exclude=["tests", "data"]),
    install_requires=req,
    python_requires=">=2.7, <3",
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Topic :: Software Development",
        "Topic :: Scientific/Engineering",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7"
    ]
)
