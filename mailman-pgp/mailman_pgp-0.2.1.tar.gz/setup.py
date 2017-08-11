import sys

from setuptools import find_packages, setup

if sys.hexversion < 0x30500f0:
    print('Mailman requires at least Python 3.5')
    sys.exit(1)

from importlib.machinery import SourceFileLoader

_init = SourceFileLoader('__init__',
                         'src/mailman_pgp/__init__.py').load_module()

setup(
        name='mailman_pgp',
        version=_init.__version__,
        description='A PGP plugin for the GNU Mailman mailing list manager',
        long_description="""\
A plugin for GNU Mailman that adds encrypted mailing lists via PGP/MIME.""",
        url='https://gitlab.com/J08nY/mailman-pgp',
        author=_init.__author__,
        author_email='johny@neuromancer.sk',
        license=_init.__license__,
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Intended Audience :: System Administrators',
            'Operating System :: POSIX',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Topic :: Communications :: Email :: Mailing List Servers',
        ],
        keywords='email pgp',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        include_package_data=True,
        zip_safe=False,
        python_requires='>=3.5',
        install_requires=[
            'mailman>=3.2.0a1',
            'PGPy>=0.4.2',
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
        test_suite='nose2.collector.collector',
        dependency_links=[
            'https://github.com/J08nY/PGPy/archive/dev.zip#egg=PGPy-0.4.2',
            'https://gitlab.com/J08nY/mailman/repository/archive.tar.gz?ref=plugin#egg=mailman-3.2.0a1'
        ]
)
