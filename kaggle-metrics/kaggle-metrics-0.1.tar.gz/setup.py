from distutils.core import setup


classifiers = [
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Topic :: Scientific/Engineering',
    ]

setup(
  name = 'kaggle-metrics',
  packages = ['kaggle_metrics'], # this must be the same as the name above
  version = '0.1',
  description = 'Metrics for Kaggle competitions',
  author = 'Krzysztof Joachimiak',
  author_email = 'joachimiak.krzysztof@gmail.com',
  url = 'https://github.com/krzjoa/kaggle-metrics', # use the URL to the github repo
 # download_url = 'https://github.com/krzjoa/kaggle-metrics', # I'll explain this in a second
  keywords = ['kaggle', 'metrics'],
  classifiers=classifiers
)