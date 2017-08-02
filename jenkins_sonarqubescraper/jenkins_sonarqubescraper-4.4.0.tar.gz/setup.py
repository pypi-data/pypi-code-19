from setuptools import setup

setup(name='jenkins_sonarqubescraper',
      version='4.4.0',
      description='Sonar Qube Scraper for Jenkins',
      url='https://github.com/KMK-ONLINE/PivotalTrackerScraper',
      author='Henry Xu',
      author_email='hxu@bbmtek.com',
      license='MIT',
      packages=['SonarQubeScraper'],
      install_requires=[
          'requests',
      ],
      scripts=['bin/sonar-analysis'],
      zip_safe=False)