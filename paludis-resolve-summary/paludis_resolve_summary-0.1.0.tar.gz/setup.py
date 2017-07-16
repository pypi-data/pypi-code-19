from setuptools import setup, find_packages

version_parts = (0, 1, 0)
version = '.'.join(map(str, version_parts))

setup(
    name='paludis_resolve_summary',
    version=version,
    packages=find_packages(exclude=['unit', 'unit.*']),
    entry_points={
        'console_scripts': [
            'paludis_resolve_summary = paludis_resolve_summary:summary',
        ]
    },
    install_requires=[
        'golgi',
    ],
)
