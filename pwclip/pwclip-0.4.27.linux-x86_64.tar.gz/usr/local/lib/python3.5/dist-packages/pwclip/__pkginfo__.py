"""pwclip packaging information"""
from os import getcwd, path, name as osname

modname = distname = 'pwclip'
numversion = (0, 4, 27)
version = '.'.join([str(num) for num in numversion])
provides = ['pwclip']
install_requires = [
    'pyusb', 'PyYAML', 'argcomplete', 'netaddr',
    'psutil', 'python-gnupg', 'python-yubico', 'paramiko']
lic = 'GPL'
description = "gui to temporarily save passwords to system-clipboard"
mailinglist = ""
author = 'Leon Pelzer'
author_email = 'mail@leonpelzer.de'
download_url = 'https://pypi.python.org/pypi/pwclip/%s#downloads'%version
classifiers = ['Development Status :: 4 - Beta',
               'Environment :: Console',
               'Environment :: MacOS X',
               'Environment :: Win32 (MS Windows)',
               'Environment :: X11 Applications',
               'Intended Audience :: Developers',
               'Intended Audience :: End Users/Desktop',
               'Intended Audience :: System Administrators',
               'Intended Audience :: Information Technology',
               'License :: OSI Approved :: GNU General Public License (GPL)',
               'Operating System :: OS Independent',
               'Programming Language :: Python :: 3',
               'Topic :: Security',
               'Topic :: Utilities',
               'Topic :: Desktop Environment',
               'Topic :: System :: Systems Administration']
try:
    with open(path.join(getcwd(), 'README.rst'), 'r') as rfh:
        readme = rfh.read()
except OSError:
    readme = ''

long_desc = (readme)

scripts = [path.join('bin', 'pwclip')]

entry_points = {
    'gui_scripts': ['pwclip = pwclip.__init__:pwclip'],
    'console_scripts': ['pwclip = pwclip.__init__:pwclip']}
