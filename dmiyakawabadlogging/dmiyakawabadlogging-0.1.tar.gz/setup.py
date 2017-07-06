from setuptools import setup

setup(name='dmiyakawabadlogging',
      version='0.1',
      author='Daisuke Miyakawa',
      author_email='d.miyakawa+badlogging@gmail.com',
      description='Demonstrates bad logging strategy',
      long_description='Demonstrates bad logging strategy',
      packages=['dmiyakawabadlogging'],
      package_data={'dmiyakawabadlogging': ['README.rst']},
      include_package_data=True,
      license='Apache License 2.0',
      url='https://github.com/dmiyakawa/python_bad_logging',
      classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3'])
