from setuptools import setup

setup(name='nimblehelper',
      version='0.6.3',
      description='Nimble Infrastructure Helper',
      author='Brendan Kamp',
      author_email='brendan@tangentsolutions.co.za',
      license='MIT',
      packages=['nimblehelper'],
      install_requires=[
          'djangorestframework',
          'requests',
          'django'
      ],
      zip_safe=False)
