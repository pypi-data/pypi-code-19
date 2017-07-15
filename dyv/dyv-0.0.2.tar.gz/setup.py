from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()

version = '0.0.2'

setup(
    name='dyv',
    version=version,
    description="DYV",
    long_description=README,
    classifiers=[
    ],
    keywords='dyv',
    author='Me',
    author_email='me@example.org',
    url='https://example.org',
    license='LGPL v3',
    py_modules=['dyv'],
    include_package_data=True,
    packages=find_packages('templates'),  # include all packages under templates
    package_dir={'': 'templates'},  # tell distutils packages are under templates
    install_requires=[
        'click',
        'ConfigParser',
        'lxml',
        'prettytable',
        'jinja2',
    ],
    entry_points='''
        [console_scripts]
        dyv=dyv:main
    ''',
)
