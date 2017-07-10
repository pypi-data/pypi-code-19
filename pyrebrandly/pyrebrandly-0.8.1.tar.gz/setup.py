from distutils.core import setup

setup(
    name='pyrebrandly',
    version='0.8.1',
    packages=['pyrebrandly'],
    url='https://github.com/ElectroCode/pyrebrandly',
    license='MIT',
    author='Ken Spencer',
    author_email='ken@electrocode.net',
    description='Interfaces with the Rebrandly.com API',
    install_requires=[
        'requests>=2.10.0'
    ],
    classifiers = [
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ]
)
