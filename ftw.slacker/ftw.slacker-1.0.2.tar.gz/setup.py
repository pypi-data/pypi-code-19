from setuptools import setup, find_packages
import os

version = '1.0.2'

tests_require = [
    'plone.app.testing'
]

setup(
    name='ftw.slacker',
    version=version,
    description='Uses webhooks to post messages into a slack channel.',
    long_description=(open('README.rst').read() + '\n' +
                      open(os.path.join('docs', 'HISTORY.txt')).read()),
    classifiers=[
        'Framework :: Plone',
        'Framework :: Plone :: 4.3',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    keywords='ftw slacker slack webhoock api',
    author='4teamwork AG',
    author_email='mailto:info@4teamwork.ch',
    url='https://git.4teamwork.ch/ftw/ftw.slacker',
    license='GPL2',

    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['ftw'],
    include_package_data=True,
    zip_safe=False,

    install_requires=[
        'setuptools',
        'Plone',
        'requests',
    ],
    tests_require=tests_require,
    extras_require=dict(tests=tests_require),
    entry_points="""
    # -*- Entry points: -*-
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
