from distutils.core import setup
setup(
    name='wxyEllen',
    package_dir = {
        'wxyEllen': 'wxyEllen',
        'wxyEllen.neo4j': 'wxyEllen/neo4j',
        'wxyEllen.mongo': 'wxyEllen/mongo',
        'wxyEllen.redis': 'wxyEllen/redis'
    },
    packages=['wxyEllen','wxyEllen.neo4j', 'wxyEllen.mongo', 'wxyEllen.redis'],
    version='0.0.5',
    description='some database',
    author='wangxiaoyu',
    author_email='wangxiaoyu.wangxiaoyu@@gmail.com',
    license='MIT',
    install_requires=[
        'pymongo',
        'py2neo'
    ],
    url='https://github.com/netsmallfish1977/wxyEllen',
    download_url='https://github.com/netsmallfish1977/wxyEllen/tarball/0.0.5',
    keywords=['wxy', 'Ellen', 'database', 'redis', 'mongo', 'neo4j'],
    classifiers=[],
)
