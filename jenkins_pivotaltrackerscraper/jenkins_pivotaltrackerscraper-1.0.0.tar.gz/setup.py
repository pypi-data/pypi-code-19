from setuptools import setup

setup(name='jenkins_pivotaltrackerscraper',
      version='1.0.0',
      description='Pivotal Tracker Scraper for Jenkins',
      url='https://github.com/KMK-ONLINE/PivotalTrackerScraper',
      author='Henry Xu',
      author_email='hxu@bbmtek.com',
      license='MIT',
      packages=['PivotalTrackerScraper'],
      install_requires=[
          'gitpython',
          'requests',
      ],
      scripts=['bin/track-and-parse-stories'],
      zip_safe=False)