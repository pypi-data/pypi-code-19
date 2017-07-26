from setuptools import setup, find_packages

setup(name='datasploit',
      version='1.0',
      description='A framework to perform various OSINT techniques, aggregate all the raw data, and give data in multiple formats.',
      url='https://github.com/DataSploit/datasploit',
      author='Shubham Mittal, Sudhanshu Chauhan, Kunal Aggarwal',
      author_email='upgoingstaar@gmail.com',
      license='GPLv3',
      packages=find_packages("."),
      install_requires=['anyjson==0.3.3','BeautifulSoup==3.2.1','beautifulsoup4==4.4.1','billiard==3.3.0.23','bs4==0.0.1','clearbit==0.1.4','config==0.3.9','dnspython==1.14.0','future==0.15.2','idna==2.1','ipwhois==0.15.1','json2html==1.0.1','lxml==3.6.0','piplapis-python==5.1.0','pymongo==3.3.0','python-Wappalyzer==0.2.2','python-whois==0.6.2','pytz==2016.6.1','requests==2.10.0','requests-file==1.4','simplejson==3.8.2','tldextract==2.0.1','tqdm==4.7.6','termcolor','tweepy==3.5.0'],
      entry_points = {
	'console_scripts': [
   		'datasploit_config = datasploit.datasploit_config:edit',
        ],
      },
      zip_safe=False)
