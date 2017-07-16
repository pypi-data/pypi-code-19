from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '0.1.1'

setup(
    name='dyv',
    version=version,
    description="DYV",
    long_description=README,
    classifiers=[    ],
    keywords='dyv',
    author='Me',
    author_email='me@example.org',
    url='https://example.org',
    license='LGPL v3',
    zip_safe=True,
    py_modules=['dyv'],
    include_package_data=True,
    packages=['dyv'],
    package_dir={'dyv': 'templates'},
    install_requires=[
        'click',
        'lxml',
        'prettytable',
        'jinja2',
        'configobj',
    ],
    entry_points='''
        [console_scripts]
        dyv=dyv:main
    ''',
)
