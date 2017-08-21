from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='fixwhitespace',
      author='honzo0481',
      author_email='gonzalesre@gmail.com',
      description='Fix whitespace in files',
      entry_points={
        'console_scripts': [
            'fixwhitespace=fixwhitespace:main'
        ]
      },
      include_package_data=True,
      license='MIT',
      long_description=readme(),
      packages=['fixwhitespace'],
      setup_requires=['pytest-runner'],
      tests_require=['pytest'],
      url='https://github.com/honzo0481/fixwhitespace',
      version='0.1',
      zip_safe=False,
      )
