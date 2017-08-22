from distutils.core import setup

setup(
    name="vkl",
    version="2017.08.22",
    description="vkl - a better ls-experience",
    author="Karl Voit",
    author_email="tools@Karl-Voit.at",
    url="https://github.com/novoid/vkl",
    download_url="https://github.com/novoid/vkl/zipball/master",
    keywords=["file managing", "file management", "files", "shell"],
    install_requires=["os", "logging", "time", "sys", "optparse", "datetime"],
    long_description="""\
vkl
-----------------------------
This tool lists the current directory content in various metric
GNU ls does not provide.

Options:
  -h, --help         show this help message and exit
  -l, --log          displays directory content by a pseudo logarithmic time
                     (default option)
  -m, --mtime        sort items using modification time (default option)
  -c, --ctime        sort items using change time
  -a, --atime        sort items using access time
  -p, --primitivels  use primitive output of directory rather than using GNU
                     ls
  -d DELEGATE, --delegate=DELEGATE
                     delegate additional arguments to ls command
  --debug            enable (senseless) debug output
"""
)
