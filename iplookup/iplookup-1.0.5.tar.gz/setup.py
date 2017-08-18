from distutils.core import setup
setup(
  name = 'iplookup',
  packages = ['iplookup'], # this must be the same as the name above
  version = '1.0.5',
  download_url = 'https://github.com/dalgibbard/iplookup/archive/1.0.5.tar.gz',
  description = 'Module for looking up IPs from Domain Names',
  long_description='''
iplookup
========
A small python module which accepts a single domain as a string, or multiple domains as a list, and returns a list of associated IPs (from both A record and CNAMEs).

* For domains with multiple A records (RRDNS), all A record IPs are returned
* IPv6 AAAA records are currently _NOT_ returned.
* For domains which are CNAMEs, the IP of the CNAME is returned
* If you give it an IP, it will return the IP back (so mixed lists are OK too)

Install::
  pip install iplookup

Usage::
  from iplookup import iplookup

  ip = iplookup.iplookup

  print(ip(["google.com", "example.com"]))

  print(ip("yahoo.com"))

''',
  author = 'Darren Gibbard',
  author_email = 'dalgibbard@gmail.com',
  url = 'https://github.com/dalgibbard/iplookup', # use the URL to the github repo
  keywords = "dns ip lookup iplookup", # arbitrary keywords
  install_requires = [
    "dnspython",
  ],
  classifiers = [
    'Development Status :: 4 - Beta',
    "Intended Audience :: Developers",
    "License :: OSI Approved :: BSD License",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2.7",
    "Programming Language :: Python :: 3",
    "Topic :: Software Development :: Libraries :: Python Modules",
  ],
  license='BSD',
)
