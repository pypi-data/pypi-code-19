from setuptools import setup

setup(name='jenkins_sonarqubescraper',
      version='1.0.0',
      description='Sonar Qube Scraper for Jenkins',
      url='https://github.com/KMK-ONLINE/PivotalTrackerScraper',
      author='Henry Xu',
      author_email='hxu@bbmtek.com',
      license='MIT',
      packages=['SonarQubeScraper'],
      scripts=['bin/sonar_analysis'],
      zip_safe=False)