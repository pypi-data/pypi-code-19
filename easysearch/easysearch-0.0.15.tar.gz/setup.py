from setuptools import setup


setup(
    name='easysearch',
    description='Machine learning library for Easysearch',
    packages=[
        'easysearch',
        'easysearch.doc2vec',
        'easysearch.doc2vec.train',
        'easysearch.lda',
        'easysearch.lda.train',
        'easysearch.solr',
        'easysearch.utils'
    ],
    install_requires=[
        'gensim>=2.3.0',
        'numpy>=1.13.1',
        'SolrClient>=0.2.1'
    ],
    version='0.0.15',
    author='Pedro Castro',
    author_email='pedro.castro@dataeasy.com.br',
    url='http://github.com/DataEasy/easysearch'
)
