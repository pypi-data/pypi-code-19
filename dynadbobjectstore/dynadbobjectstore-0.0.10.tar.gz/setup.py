from setuptools import setup
import sys
import os

version = None

if sys.argv[-2] == '--version' and 'sdist' in sys.argv:
    version = sys.argv[-1]
    sys.argv.pop()
    sys.argv.pop()

if 'sdist' in sys.argv and not version:
    raise Exception("Please set a version with --version x.y.z")

if not version:
    if 'sdist' in sys.argv:
        raise Exception("Please set a version with --version x.y.z")
    else:
        path_pkg_info = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'PKG-INFO')
        if os.path.isfile(path_pkg_info):
            with open(path_pkg_info, 'r')as f:
                for l in f.readlines():
                    if 'Version' in l:
                        _, version = l.split(' ')
        else:
            print("WARNING: cannot set version in custom setup.py")

print("version: %s" % version)

setup(
    name='dynadbobjectstore',
    version=version,
    url='https://github.com/erwan-lemonnier/dynamodbobjectstore',
    license='BSD',
    author='Erwan Lemonnier',
    author_email='erwan@lemonnier.se',
    description='Store and retrieve python objects stored in a DynamoDB table.',
    install_requires=[
        'boto',
    ],
    tests_require=[
        'boto',
    ],
    test_suite='nose.collector',
    py_modules=['dynadbobjectstore'],
    platforms='any',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
