from setuptools import setup


with open('.git/refs/heads/master') as f:
    git_hash = f.read().strip()[:7]


GIT_VERSION = int(git_hash, 16)
MAJOR_VERSION = '0'
MINOR_VERSION = '1'

VERSION = '{major}.{minor}.dev{dev}'.format(
    major=MAJOR_VERSION, minor=MINOR_VERSION, dev=GIT_VERSION)


setup(
    name='ngramgraphs',
    version=VERSION,
    description='Create N Gram Graphs and export them to images or PDF files',
    author='Simon Liedtke',
    author_email='sliedtke@uni-bremen.de',
    url='https://gitlab.informatik.uni-bremen.de/sliedtke/ngramgraphs',
    packages=['ngramgraphs'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Topic :: Text Processing',
    ],
)
