from setuptools import setup, find_packages

version_parts = (0, 6, 2)
version = '.'.join(map(str, version_parts))

setup(
    name='tubbs',
    description='ebnf-based text objects',
    version=version,
    author='Torsten Schmits',
    author_email='torstenschmits@gmail.com',
    license='MIT',
    url='https://github.com/tek/tubbs',
    include_package_data=True,
    packages=find_packages(
        exclude=['unit', 'unit.*', 'integration', 'integration.*']),
    install_requires=[
        'amino>=10.3.0',
        'ribosome>=10.3.5',
        'hues',
        'tatsu',
        'regex',
    ],
    tests_require=[
        'kallikrein',
    ],
)
