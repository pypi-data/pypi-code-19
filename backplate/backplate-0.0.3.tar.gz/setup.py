
from setuptools import setup

setup(
    name='backplate',
    version='0.0.3',
    description='RESTful API Helpers',
    author='Peter Boyer',
    author_email='petertboyer@gmail.com',
    url='https://github.com/studioarmix/backplate',
    packages=['backplate'],
    license='MIT',
    install_requires=[
        'flask',
        'flask-restful',
        'flask-cors',
        'flask-api'
    ]
)
