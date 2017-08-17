from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='django-utf8field',
      version='0.0.1',
      description='Add UTF-8 Validation to a Django FileField',
      long_description=readme(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: Apache Software License',
          'Framework :: Django',
      ],
      author='Stef Bastiaansen',
      author_email='stef@megasnort.com',
      url='https://github.com/megasnort/django-utf8field',
      download_url='https://github.com/megasnort/django-utf8field/archive/v0.0.1.tar.gz',
      packages=['utf8field'],
      keywords='django utf-8',
      license='Apache',
      )
