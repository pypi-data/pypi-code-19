from setuptools import setup

setup(
    name='JekPost',
    version='1.0',
    author='Arjun Krishna Babu',
    author_email='arjunkrishnababu96@gmail.com',
    packages=['jekpost'],
    url='https://github.com/arjunkrishnababu96/jekpost',
    license='LICENSE.txt',
    description='Package to ease the process of creating a new Jekyll post',
    long_description=open('README.txt').read(),
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts':  [
            'jekpost_create = jekpost.jekpost_create:main'
        ],
    }
)
