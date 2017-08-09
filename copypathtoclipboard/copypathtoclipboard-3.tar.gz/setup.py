from setuptools import setup

setup(name='copypathtoclipboard',
      version='3',
      description='Copy path to clipboard :)',
      url='http://none.com',
      author='Walter Mastrangelo',
      author_email='walterjmas@gmail.com',
      license='MIT',
      packages=['copypathtoclipboard'],
      install_requires=[
          'pyperclip'
          ],
      scripts=['bin/copypathtoclipboard'],
      zip_safe=False)