from setuptools import setup


setup(
  name = 'geepal',
  version = '0.1.7',
  author = 'Eric Allen Youngson',
  author_email = 'eayoungs@gmail.com',
  packages = ['geepal'], # this must be the same as the name above
  scripts = ['bin/invoice.py'],
  description = 'From Google Calendar to dataframes',
  url = 'https://github.com/eayoungs/Gcal', # use the URL to the github repo
  download_url = 'https://github.com/eayoungs/Gcal/archive/master.zip',
  keywords = ['time', 'tracking', 'calendar', 'dataframe'], # arbitrary keywords
  classifiers = [],
  license = 'LICENSE.txt',
  long_description=open('README.txt').read(),
  install_requires = [
    "google-api-python-client>=1.6.1",
    "oauth2client>=4.0.0",
    "httplib2>=0.9.2",
    "iso8601>=0.1.11",
    "matplotlib>=2.0.0",
    "pandas>=0.19.2",
    "python-dateutil>=2.5.3",
    "pytz>=2016.4",
    "tzlocal>=1.3",
    "parsedatetime>=2.1",
    "jupyter>=1.0.0",
    "pytest>=3.0.6",
    "regex>=2016.7.21",
    "pyinvoice>=0.1.7",
    ],
)
