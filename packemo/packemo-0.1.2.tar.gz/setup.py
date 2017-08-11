from distutils.core import setup

# If the reStructuredText syntax is used in the long_description field (and
# docutils is installed), use `python setup.py check --restructuredtext` to
# check if the the syntax is fine.
description = """\
Description
===========

This is the description of the **packemo** package.

"packemo" means package demo, which is a tiny Python package
containing some rather simple modules and a ``setup.py`` file.

This package tries to give a simple demonstration of how Python
packages are organized and how to write a ``setup.py``.

"""

# You can use `python setup.py install --record ./record.txt` to know which
# files are created and where they are, and can use the MANIFEST file to see
# which files in the source are used to install the package.
# And to remove them thoroughly, you can use `cat files.txt | xargs rm -rf`.
# (on Windows?)
setup(
    # Actually the name here is NOT the package name which is imported into 
    # Python files. But if pip is used, this name needs to be told to pip.
    name="packemo",
    version="0.1.2",

    author="psrit",
    author_email="xiaojx13@outlook.com",
    url="https://pypi.python.org/pypi/packemo/",

    long_description=description,

    classifiers=[
        "Environment :: Console",
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        # "Natural Language :: Chinese (Simplified)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: Unix",
        "Programming Language :: Python",
        "Topic :: Education",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    # -------------------------------------------------------------------------
    # All the packages listed here will be in the "root" package if they are
    # installed by `python setup.py install`.
    # (Every directory listed in `sys.path` contributes modules to the root
    # package, e.g. `D:\Anaconda3\envs\pkg_demo\Lib\site-packages\`)
    # To use the packages, just import the names listed below (not the `name`
    # field of setup()).
    # -------------------------------------------------------------------------
    packages=[
        "packemo",
        "packemo.subpackage1",
        "packemo.subpackage1.subsubpackage11",
        "packemo.subpackage2"
    ],

    # -------------------------------------------------------------------------
    # The keys are package names, and the values are directory names relative
    # to the DISTRIBUTION ROOT. If the key being empty (i.e. ""), the directory
    # represented by the corresponding value will be put directly into the
    # "root" package.
    # -------------------------------------------------------------------------
    package_dir={"packemo": "src"},

    # -------------------------------------------------------------------------
    # NOTE: the following settings are also OK, but the structure of the
    # resulting package will be different, like
    #     packemo
    #        |
    #        +-- subpackage1
    #        +-- subsubpackage11
    #        +-- subpackage2
    # which means that `subsubpackage11` must be refered to through
    # `packemo.subsubpackage11` instead of
    # `packemo.subpackage1.subsubpackage11` (therefore src/app.py must be
    # modified).
    # See installation record for some details.
    # -------------------------------------------------------------------------
    # packages=[
    #     "packemo",
    #     "packemo.subpackage1",
    #     "packemo.subsubpackage11",
    #     "packemo.subpackage2"
    # ],
    # package_dir={
    #     "packemo": "src",
    #     "packemo.subsubpackage11": "src/subpackage1/subsubpackage11"
    # },

    package_data={
        # "": ["data/*"], # WON'T WORK
        "packemo": ["package_data/*"],
        "packemo.subpackage1": ["subpackage1_data/*"],
        "packemo.subpackage1.subsubpackage11": [
            "subsubpackage11_data/*"],
        "packemo.subpackage2": ["subpackage2_data/*"],
    },
    # data_files=[]

    # -------------------------------------------------------------------------
    # All scripts listed here will be in the Python's Script directory,
    # e.g. `D:\Anaconda3\envs\pkg_demo\Scripts\` for an environment called
    # pkg_demo of Anaconda. Therefore these scripts can be used directly from
    # the terminal.
    # -------------------------------------------------------------------------
    scripts=[
        # "src/app.py",
        "scripts/packemo_test.py",
    ],
)
