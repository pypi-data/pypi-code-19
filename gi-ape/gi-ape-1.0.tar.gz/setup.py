from setuptools import setup, find_packages
setup(
    name = "gi-ape",
    version = "1.0",
    author = "Christopher Schröder and Sven Rahmann",
    author_email = "christopher.schroeder@tu-dortmund.de",
    long_description=__doc__,
    license = "MIT",
    url = "https://bitbucket.org/christopherschroeder/ape",
    packages=find_packages(),
    py_modules = ["run"],
    package_data={
        'ape': 'ape/*'},
    include_package_data=True,
    zip_safe=False,
    entry_points = {"console_scripts": [
                        "ape = ape.ape:main"
                    ]},
    install_requires=[
        'pysam',
        'numpy',
        'snakemake',
    ],
    classifiers = [
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Framework :: Flask",
        "Environment :: Web Environment",
        "Intended Audience :: Science/Research"]
)
