#!/usr/bin/env python

from setuptools import setup

setup(
    name="nfq-conductor",
    description="NFQ Solutions process manager",
    version="0.2.1",
    author="NFQ Solutions",
    author_email="solutions@nfq.es",
    packages=[
        'nfq',
        'nfq.conductor',
        'nfq.logwrapper'
        ],
    zip_safe=False,
    install_requires=['psutil', 'zmq', 'tornado', 'sqlalchemy'],
    include_package_data=True,
    setup_requires=[],
    tests_require=[],
    entry_points={
        'console_scripts': [
            'nfq-runner=nfq.logwrapper.runner:run',
            'nfq-conductor=nfq.conductor.server:run',
            'nfq-conductor-daemon=nfq.conductor.daemon:run',
            'nfq-conductor-submit=nfq.conductor.submit:run']
        }
    )
