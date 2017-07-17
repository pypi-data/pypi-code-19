from setuptools import setup

VERSION = '0.0.2'
with open('README.md') as f:
    long_descriptioin = f.read()
setup(name='panhello',
      version=VERSION,
      description=long_descriptioin,
      classifiers=[],
      keywords='test hello',
      author='Cppowboy',
      author_email='panyx93@163.com',
      url='https://pypi.python.org/pypi/panhello',
      license='MIT',
      pacakages=['panhello'],
      include_package_data=True,
      zip_safe=True,
      install_requires=['pandas', 'numpy'],
      )
