import os
import io
from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()


def get_path(*args):
    return os.path.join(os.path.dirname(__file__), *args)


def read_from(filepath):
    with io.open(filepath, 'rt', encoding='utf8') as f:
        return f.read()


def get_requirements(filename='requirements.txt'):
    data = read_from(get_path(filename))
    lines = map(lambda s: s.strip(), data.splitlines())
    return [l for l in lines if l and not l.startswith('#')]


setup(
    name='creh-urltrace',
    version='0.0.10',
    packages=find_packages(),
    description='Url trace application',
    long_description=README,
    author='Enrique',
    author_email='enrique@crehana.com',
    url='https://bitbucket.org/crehana/creh-urltrace',
    license='MIT',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    install_requires=get_requirements(),
    test_suite="runtests.runtests",
)