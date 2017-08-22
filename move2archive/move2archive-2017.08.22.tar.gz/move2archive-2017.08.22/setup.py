from distutils.core import setup

setup(
    name="move2archive",
    version="2017.08.22",
    description="Managing event-related files in a folder hierarchy like <ARCHIVE>/2013/2013-05-17 Event name/",
    author="Karl Voit",
    author_email="tools@Karl-Voit.at",
    url="https://github.com/novoid/move2archive",
    download_url="https://github.com/novoid/move2archive/zipball/master",
    keywords=["file managing", "file management", "files", "date", "time", "time-stamps"],
    install_requires=["os", "re", "logging", "time", "sys", "optparse", "datetime", "shutil", "fnmatch", "readline"],
    long_description="""\
move2archive
-----------------------------
This script moves items (files or directories) containing ISO datestamps
like "YYYY-MM-DD" into a directory stucture for the corresponding year.

You define the base directory either in this script (or using the
command line argument "--archivedir"). The convention is e.g.:

        <archivepath>/2009
        <archivepath>/2010
        <archivepath>/2011

By default, this script extracts the year from the datestamp of
each file and moves it into the corresponding directory for its year:

     m2a 2010-01-01_Jan2010.txt 2011-02-02_Feb2011.txt
... moves "2010-01-01_Jan2010.txt" to "<archivepath>/2010/"
... moves "2011-02-02_Feb2011.txt" to "<archivepath>/2011/"

OPTIONALLY you can define a sub-directory name with option "-d DIR". If it
contains no datestamp by itself, a datestamp from the first file of the
argument list will be used. This datestamp will be put in front of the name:

     m2a  -d "2009-02-15 bar"  one two three
... moves all items to: "<archivepath>/2009/2009-02-15 bar/"

     m2a  -d bar  2011-10-10_one 2008-01-02_two 2011-10-12_three
... moves all items to: "<archivepath>/2011/2011-10-10 bar/"

If you feel uncomfortable you can simulate the behavior using the "--dryrun"
option. You see what would happen without changing anything at all.
"""
)
