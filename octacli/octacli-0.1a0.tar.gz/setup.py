from setuptools import setup, find_packages

setup(
    name='octacli',
    version='0.1a',
    py_modules=['octacli', 'tokens', 'namespace', 'user', 'service', 'policy', 'alert'],
    install_requires=[
        'Click',
        'requests',
        'tabulate',
    ],
    entry_points='''
        [console_scripts]
        octacli=octacli:octacli
    ''',
)
