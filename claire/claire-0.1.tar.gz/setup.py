from setuptools import setup

setup(
    name="claire",
    version='0.1',
    py_modules=['hack'],
    install_requires=[
        'Click',
        'Clarifai',
        'Validators',
    ],
    entry_points='''
        [console_scripts]
        claire=hack:cli
    ''',
)
