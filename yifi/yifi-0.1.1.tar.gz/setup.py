import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__),fname)).read()

setup(
    name = "yifi",
    version = "0.1.1",
    author = "vitaminC",
    author_email = "dmakhil@gmail.com",
    description = ("browse yifi on your command line"),
    entry_points={'console_scripts':['yifi=yifi.command_line:main']},
    license = "GPLv3",
    keywords = "yifi torrent download",
    packages = ['yifi'],
    long_description = read('help.txt'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Python Software Foundation License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Topic :: Communications :: Email',
        'Topic :: Office/Business',
        'Topic :: Software Development :: Bug Tracking',
    ],
)

