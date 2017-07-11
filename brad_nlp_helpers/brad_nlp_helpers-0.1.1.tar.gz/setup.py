from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()


setup(name='brad_nlp_helpers',
      version='0.1.1',
      description='Python based packages for NLP EDA',
      url='https://github.com/bradaallen/nlp_helper',
      author='Brad Allen',
      author_email='bradaallen@gmail.com',
      license='MIT',
      install_requires=[
          'pandas',
          'nltk',
          'collections',
      ],
      packages=['brad_nlp_helpers'],
      zip_safe=False)
