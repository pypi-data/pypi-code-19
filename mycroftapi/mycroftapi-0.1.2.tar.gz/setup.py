from setuptools import setup

setup(
    name='mycroftapi',
    packages=['mycroftapi'],
    install_requires=['websocket-client==0.44.0'],
    version='0.1.2',
    description='a library to communicate with Mycroft API',
    author='Brian Hopkins',

    url='https://github.com/Geeked-Out-Solutions/mycroft_api.git',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Home Automation',
        'Topic :: Software Development :: Libraries :: Python Modules'
        ]
)
