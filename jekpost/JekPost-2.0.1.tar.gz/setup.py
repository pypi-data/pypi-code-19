from setuptools import setup

setup(
    name='JekPost',
    version='2.0.1',
    author='Arjun Krishna Babu',
    author_email='arjunkrishnababu96@gmail.com',
    packages=['jekpost'],
    url='https://github.com/arjunkrishnababu96/jekpost',
    license='MIT',
    description='Package to ease the process of creating a new Jekyll post',
    long_description=open('README.rst').read(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Utilities",
    ],
    entry_points={
        'console_scripts':  [
            'jekpost=jekpost.jekpost:main',
        ],
    }
)
