from setuptools import setup

def readme():
    with open('README.md','w') as f:
        return f.read()


setup(name='SalesForceSession',
      version='0.1b',
      description='A wrapper for simple-salesforce that creates a session and build valid SQL queries by passing query params rather than the raw sql.',
      classifiers=[
         'Development Status :: 4 - Beta',
         'License :: OSI Approved :: MIT License',
         'Intended Audience :: Developers',
         'Intended Audience :: System Administrators',
         'Operating System :: OS Independent',
         'Topic :: Internet :: WWW/HTTP',
         'Programming Language :: Python :: 2.6',
         'Programming Language :: Python :: 2.7'
      ],
      keywords='salesforce simple-salesforce sessions',
      url='https://github.com/configuresystems/salesforce-session',
      author='John Martin',
      author_email='john.martin@configure.systems',
      license='MIT',
      py_modules=['salesforce_session'],
      install_requires=[
          'simple-salesforce',
          ],
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose']
      )
