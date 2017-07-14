from setuptools import find_packages, setup

setup(
    name='mailman_pgp',
    version='0.1',
    description='A PGP plugin for the GNU Mailman mailing list manager',
    long_description="""\
A plugin for GNU Mailman that adds encrypted mailing lists via PGP/MIME.""",
    url='https://gitlab.com/J08nY/mailman-pgp',
    author='Jan Jancar',
    author_email='johny@neuromancer.sk',
    license='GPLv3',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: System Administrators',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Communications :: Email :: Mailing List Servers',
    ],
    keywords='email pgp',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'mailman>=3.1.1',
        'PGPy',
        'atpublic',
        'flufl.lock',
        'sqlalchemy',
        'zope.interface',
        'zope.event'
    ],
    tests_require=[
        'flufl.testing',
        'parameterized',
        'nose2'
    ],
    test_suite='nose2.collector.collector'
)
