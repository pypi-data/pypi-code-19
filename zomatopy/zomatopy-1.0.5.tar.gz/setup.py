from setuptools import setup

setup(
    name='zomatopy',
    packages=['zomatopy'],
    version='1.0.5',
    url='https://github.com/sharadbhat/Zomatopy',
    description='A simple python wrapper for the Zomato API',
    author='Sharad Bhat',
    license='MIT',
    classifiers=[
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='Zomato',
    install_requires=[
        'requests==2.11.1'
    ]
)
