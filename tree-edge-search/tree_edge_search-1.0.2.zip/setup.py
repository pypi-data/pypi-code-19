from distutils.core import setup

setup(
    name = 'tree_edge_search',
    packages = ['tree_edge_search'],
    version = '1.0.2',
    description = 'A NetworkX package which computes the edge search number of a tree',
    long_description = 'A NetworkX graph theory package that calculates the edge search number of a tree. The algorithm is based off of The Complexity of Searching a Graph by N. Megiddo et. al. The algorithm runs in O(nlog(n)) and is very fast for small to mid sized trees (hundreds of vertices).',
    license = 'MIT',
    author = 'Anton Afanassiev',
    author_email = 'antonafana@yahoo.ca',
    url = 'https://github.com/Jabbath/Tree-Edge-Search-Number',
    download_url = 'https://github.com/Jabbath/Tree-Edge-Search-Number/archive/1.0.2.tar.gz',
    keywords = ['graph', 'theory', 'search', 'number', 'edge',  'pursuit', 'evasion', 'tree'],
    classifiers = ['Development Status :: 5 - Production/Stable'],
    install_requires = ['networkx']
)
