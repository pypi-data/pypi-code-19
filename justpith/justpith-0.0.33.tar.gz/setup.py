from setuptools import setup

setup(
    name = "justpith",
    version = "0.0.33",
    author = "Antonio Carisita",
    author_email = "a.caristia@gmail.com",
    description = ("Core code for justpith infrastructure"),
    license = "GPL",
    keywords = "justpith's core",
    url = "http://packages.python.org/justpith",
    packages=['justpith','justpith.rabbit', 'justpith.mongo','justpith.logger'],
    install_requires=[
          'pika','pymongo','fluent-logger'
    ],
    zip_safe=False
)
