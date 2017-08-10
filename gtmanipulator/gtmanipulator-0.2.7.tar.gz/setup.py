import setuptools

setuptools.setup(name="gtmanipulator",
                 version="0.2.7",
                 description="Manipulates GenomeStudio processed "
                             "Illumina iScan microarray data.",
                 long_description="This module contains classes and methods intended for" 
                                  "use on Illumina iScan microarray data post GenomeStudio "
                                  "processing. Additionally, a GUI implementation of the "
                                  "gtmanipulator module is also available.", 
                 url="https://github.com/TravisCouture/gtmanipulator",
                 author="Travis Couture",
                 author_email="travis.m.couture@gmail.com",
                 license="MIT",
                 packages=["gtmanipulator"],
                 install_requires=[
                    "pandas>=0.20.3",
                    "PyQt5>=0.4.4"
                 ],
                 keywords="alleles illumina Illumina iScan microarray data",
                 include_package_data=True,
                 classifiers=[
                    "Development Status :: 4 - Beta",
                    "Intended Audience :: Science/Research",
                    "License :: OSI Approved :: MIT License",
                    "Natural Language :: English",
                    "Topic :: Scientific/Engineering :: Bio-Informatics"
                 ])
