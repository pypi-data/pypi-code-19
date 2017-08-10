from setuptools import setup

setup(
    name='Zomatopy',
    packages=['Zomatopy'],
    version='1.0.4',
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
