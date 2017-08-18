import setuptools

setuptools.setup(
    name="bio-pm",
    version="0.1.0",
    url="https://github.com/ekeyme/bio-pm",

    author="Ekeyme Mo",
    author_email="ekeyme@gmail.com",
    description = "A point mutation analyzing tool for nucleotide sequence",
    keywords = "nucleotide mutation analyzing",
    long_description=open('README.rst').read(),

    packages = ["pm", ],

    license = "MIT",
    install_requires = ['biopython', ],
    classifiers= [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        "Programming Language :: Python :: 3 :: Only",
    ]
)