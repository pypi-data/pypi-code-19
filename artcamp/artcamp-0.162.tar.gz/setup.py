from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='artcamp',
      version='0.162',
      description='Query similarity between articles, orgs, and/or campaigns',
      url='http://github.com/jwilber/artcamp',
      author='Jared Wilber',
      author_email='jwilber@classy.org',
      include_package_data=True,
      license='MIT',
      packages=['artcamp'],
      package_data={'mypkg': ['data/*']},
      install_requires=[
          'gensim',
          'scikit-learn',
      ],
      zip_safe=False)
