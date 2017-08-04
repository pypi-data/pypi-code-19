# !/usr/bin/env python

from itertools import chain

from setuptools import find_packages, setup

extras_require = {
    'markdown': [
        'Markdown>=2.6,<3'
    ],
    'pipeline': [
        'django-pipeline>=1.6,<1.7',
        'libsass>=0.11,<0.13',
        'csscompressor>=0.9,<1.0',
    ],
    'raven': [
        'raven>=6.0,<6.1'
    ],
    's3': [
        'boto3>=1.4,<1.5',
    ],
    'frontmatter': [
        'PyYAML>=3,<4',
    ],
    'json': [
        'psycopg2>=2.7',
    ],
}

extras_require['all'] = list(chain(extras_require.values()))

setup(
    name='bulv1ne-django-utils',
    packages=find_packages(exclude=['tests']),
    version='0.2.0',
    description='Django utils for all kinds of situations',
    author='Niels Lemmens',
    license='MIT',
    author_email='draso.odin@gmail.com',
    url='https://github.com/bulv1ne/django-utils',
    keywords=['django', 'utils'],
    install_requires=[
        'django>=1.10,<2',
    ],
    extras_require=extras_require,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Utilities',
    ],
)
