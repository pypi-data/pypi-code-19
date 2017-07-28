import commands
from distutils.core import setup

setup(
    name='redisio',
    version='0.1',
    author='Roy',
    author_email='cf020031308@163.com',
    maintainer='Roy',
    maintainer_email='cf020031308@163.com',
    packages=['redisio'],
    url='https://github.com/cf020031308/redisio',
    keywords=['Redis', 'key-value store'],
    license='MIT',
    description='A tiny and fast redis client for script boys.',
    long_description=commands.getoutput('mdv -A README.md'),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Topic :: Database'
    ]
)
