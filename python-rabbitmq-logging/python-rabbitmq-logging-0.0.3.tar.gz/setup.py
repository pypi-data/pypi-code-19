from setuptools import setup, find_packages

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6'
]

INSTALL_REQUIRES = [
    'pika==0.10.0'
]

setup(name='python-rabbitmq-logging',
      version='0.0.3',

      url='https://github.com/aydoganserdar/python-rabbit-logging',
      description='Send logs to RabbitMQ from Python/Flask',
      keywords='logging rabbitmq logs',
      license='MIT',

      author='Serdar AYDOGAN',
      author_email="aydoganserdar@gmail.com",

      classifiers=CLASSIFIERS,
      install_requires=INSTALL_REQUIRES,
      packages=find_packages(),
      extras_require={
          'dev': ['check-manifest']
      },

      test_suite='nose.collector',
      tests_require=['nose'],
      zip_safe=True)
