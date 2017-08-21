from setuptools import setup, find_packages

setup(name='avpclient',
    version='0.5',
    description='client library for initiating distributed/async web api calls to AIDVP',
    url='https://github.com/aidvp/avpclient',
    author='AIDVP',
    author_email='aidvpservice@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['contrib','docs','test*','resources']),
    python_requires='>3.6',
    install_requires=['aiohttp','asyncio','async_timeout','pandas','uvloop','numpy','requests'],
    zip_safe=False)






