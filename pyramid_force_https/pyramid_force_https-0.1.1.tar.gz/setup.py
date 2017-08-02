import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))
readme = open(os.path.join(here, 'README.rst')).read()
changes = open(os.path.join(here, 'CHANGES.rst')).read()


requires = [
    'pyramid>=1.7',
]

setup(
    name='pyramid_force_https',
    version='0.1.1',
    description='A tween to force HTTPS.',
    long_description=readme + '\n' + changes,
    classifiers=[
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
    packages=['pyramid_force_https'],
    install_requires=requires,
    author='NiteoWeb Ltd.',
    author_email='info@niteoweb.com',
    license='BSD',
    url='https://github.com/niteoweb/pyramid_force_https',
    keywords='pyramid ssl pylons web',
    tests_require=requires,
    test_suite='pyramid_force_https',
)
