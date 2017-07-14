from setuptools import setup, find_packages

setup(
    name='django-webpack-static',
    version='0.1.2',
    description="Adds support for loading assets generated with manifest-revision-webpack-plugin",
    long_description="Adds support for loading assets generated with manifest-revision-webpack-plugin",
    url='https://bitbucket.org/cicwarsaw/django-webpack-static',
    author='Pawel Andziak (CIC)',
    author_email='andziak@cictr.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        'Django>=1.9'
    ],
    packages=find_packages(),
    keywords='webpack assets django static',
)