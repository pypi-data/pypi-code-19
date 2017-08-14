from setuptools import setup

long_description = open('README.rst').read()

setup(
    name="django-flashbriefing",
    version='0.1',
    packages=["flashbriefing"],
    include_package_data=True,
    description="Amazon Alexa Flash Briefings for Django",
    url="https://github.com/istrategylabs/django-flashbriefing",
    author="ISL",
    author_email="dev@isl.co",
    license='BSD',
    long_description=long_description,
    platforms=["any"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
