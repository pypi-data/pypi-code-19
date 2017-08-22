from setuptools import setup

setup(
    name = "pycrctrl",
    py_modules = ["pycrctrl"],
    version = "0.1",
    description = "Controller for clonk's dedicated server",
    author = "George Tokmaji",
    author_email = "tokmajigeorge@gmail.com",
    url = "https://github.com/Fulgen301/pycrctrl",
    download_url = "https://github.com/Fulgen301/pycrctrl/archive/0.1.tar.gz",
    keywords = ["clonk", "openclonk"],
    license = "ISC",
    requires = ["limnoria"],
    install_requires = ["limnoria"]
    )
