from distutils.core import setup

setup(
    name = 'dynamic_search_number',
    packages = ['dynamic_search_number'],
    version = '1.0.2',
    description = 'A NetworkX package that computes mixed search number and edge search number.',
    long_description = 'A Networkx package that can calculate mixed edge search number and edge search number. The implementation uses dynamic programming to solve the related problem of LINEAR WIDTH to compute the search parameters.',
    license = 'MIT',
    author = 'Anton Afanassiev',
    author_email = 'antonafana@yahoo.ca',
    url = 'https://github.com/Jabbath/Search-Number-Dynamic',
    download_url = 'https://github.com/Jabbath/Search-Number-Dynamic/archive/1.0.2.tar.gz',
    keywords = ['graph', 'theory', 'search', 'number', 'mixed', 'edge', 'linear', 'width' 'pursuit', 'evasion'],
    classifiers = ['Development Status :: 5 - Production/Stable'],
    install_requires = ['networkx']
)
