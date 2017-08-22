from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='lebot-cerebro',
      version='0.1.0dev1',
      description='Core engine for LeBot',
      long_description='''cerebro
=======

|CircleCI|

|codecov|

Core engine for @LeBot, A generic bot that will be able to do custom
tasks on the basis of the interaction with User.

Run Tests
---------

.. raw:: html

   <pre>nosetests</pre>

Run Start
---------

.. raw:: html

   <pre>python start.py &lt;command&gt; </pre>

List of supported Commands
--------------------------

.. raw:: html

   <pre>"how are you?", "what is the time?", "what is the date?"</pre>

.. |CircleCI| image:: https://circleci.com/gh/Le-Bot/cerebro/tree/master.svg?style=shield
   :target: https://circleci.com/gh/Le-Bot/cerebro/tree/master
.. |codecov| image:: https://codecov.io/gh/Le-Bot/cerebro/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/Le-Bot/cerebro
   ''',
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
      ],
      keywords=['Chat Bot, AI'],
      url='https://github.com/Le-Bot/cerebro',
      author='LeBot',
      author_email='sanket.upadhyay@infoud.co.in',
      license='MIT',
      packages=['cerebro'],
      install_requires=[
          'scikit-learn',
          'scipy',
          'numpy',
          'pandas',
      ],
      test_suite='nose.collector',
      tests_require=['nose'],
      include_package_data=True,
      zip_safe=False)
