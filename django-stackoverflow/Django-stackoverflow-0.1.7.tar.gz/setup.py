from setuptools import setup

setup(
    name='Django-stackoverflow',
    version='0.1.7',
    url='https://pypi.python.org/pypi?name=Stackoverflow&version=0.1.3&:action=display',
    author='FizLin',
    author_email='18818261892@163.com',
    description='Useful Django exception query with stackoverflow site',
    install_requires=[
        "Django >= 1.7",
        "requests == 2.18.3",
    ],
    packages=['Stackoverflow'],

)
