from setuptools import setup

setup(name='django-misc-helpers',
      version='0.1.11',
      description='Some django helpers',
      url='https://bitbucket.org/pi11/django-misc-helpers',
      packages=['djangohelpers'],
      package_data={'djangohelpers': ['data/*.txt']},
      author="pi11",
      author_email="webii@yandex.ru"
      # install_requires=['ipaddr'],
      )
