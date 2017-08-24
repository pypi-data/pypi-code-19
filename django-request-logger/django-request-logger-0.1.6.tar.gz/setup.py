from setuptools import setup, find_packages

setup(name='django-request-logger',
      version='0.1.6',
      description='Django middleware that logs http request information to database.',
      url='https://git.pispalanit.fi/pit/django-request-logger',
      author='Joni Saarinen',
      author_email='joni.saarinen@pispalanit.fi',
      license='MIT',
      packages=find_packages(),
      install_requires=[
          'Django',
      ],
zip_safe=False)
