from setuptools import setup

def readme():
    with open('README.rst','w') as f:
        return f.read()


setup(name='AWSGateway-Client',
      version='0.1',
      description='AWS Gateway Client',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 2.7',
          'Topic :: Text Processing :: Linguistic',
          ],
      keywords='aws gateway client for boto3',
      url='https://github.com/iamjohnnym/apigateway_client',
      author='iamjohnnym',
      author_email='j.martin0027@gmail.com',
      license='MIT',
      packages=['apigateway_client'],
      install_requires=[
          'awsrequests',
          ],
      include_package_data=True,
      zip_safe=False,
      test_suite='nose.collector',
      tests_require=['nose']
      )
