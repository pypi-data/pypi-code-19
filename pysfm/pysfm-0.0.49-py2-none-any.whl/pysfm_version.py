import pkg_resources  # part of setuptools

def get_version():
    version = pkg_resources.require("pysfm")[0].version
    # print version
    return version