from setuptools import setup

def readme():
    with open('README.rst','w') as f:
        return f.read()


setup(name='CalendarDiscovery',
      version='0.1',
      description='An expantion of datetime to get more information about a' \
                  + 'date.',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Text Processing :: Linguistic',
          ],
      keywords='calendar parser',
      url='https://github.com/iamjohnnym/discovery_calendar',
      author='iamjohnnym',
      author_email='j.martin0027@gmail.com',
      license='MIT',
      packages=['CalendarDiscovery'],
      install_requires=[
          'pandas',
          ],
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose']
      )
