from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '0.2.1'

setup(
    name='dyv',
    version=version,
    description="dyv",
    long_description=README,
    classifiers=[    ],
    keywords='dyv',
    author='me',
    author_email='me@example.org',
    url='https://example.org',
    license='LGPL v3',
    zip_safe=True,
    py_modules=['dyv'],
    include_package_data=True,
    packages=['dyv', 'odooast'],
    package_dir={'dyv': 'templates', },
    install_requires=[
        'click',
        'lxml',
        'prettytable',
        'jinja2',
        'configobj',
        'ConfigParser',
    ],
    entry_points='''
        [console_scripts]
        dyv=dyv:main
    ''',
)
