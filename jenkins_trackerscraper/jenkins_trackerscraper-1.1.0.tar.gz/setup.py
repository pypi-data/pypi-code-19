from setuptools import setup

setup(name='jenkins_trackerscraper',
      version='1.1.0',
      description='Pivotal Tracker Scraper for Jenkins',
      url='https://github.com/KMK-ONLINE/PivotalTrackerScraper',
      author='hxu',
      author_email='iosbbmautomationandi@gmail.com',
      license='MIT',
      packages=['PivotalTrackerScraper'],
      install_requires=[
          'gitpython',
          'requests',
      ],
      scripts=['bin/track-and-parse-stories'],
      zip_safe=False)