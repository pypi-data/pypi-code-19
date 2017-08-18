from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='artcamp',
      version='0.156',
      description='Query similarity between articles, orgs, and/or campaigns',
      url='http://github.com/jwilber/artcamp',
      author='Jared Wilber',
      author_email='jwilber@classy.org',
      license='MIT',
      packages=['artcamp'],
      install_requires=[
          'gensim',
          'scikit-learn',
      ],
      zip_safe=False)
