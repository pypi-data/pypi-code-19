
import os

try:
    from setuptools import setup
    from setuptools import find_packages
except:
    from distutils.core import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


def read_requirements(fname):
    f = open(os.path.join(os.path.dirname(__file__), fname))
    return filter(lambda f: f != '', map(lambda f: f.strip(), f.readlines()))


setup(
    zip_safe=False,
    name="django_pre_post",
    version="1.0.0",
    author="Silly Inventor",
    author_email="SillyInventor@gmail.com",
    description="This package provides a framework for surveys and questionnaires",
    keywords="test, pre-post, questionnaire, survey",
    packages=find_packages(),
    long_description=read('README.md'),
    install_requires=[
                      'Django==1.10.6',
                      'django-bootstrap3==8.2.2',
                      ],
    dependency_links=[
        'https://github.com/CSnap/django_teams/tarball/master',
    ],
    test_suite="dummy",
    include_package_data=True,
)
