#!/usr/bin/env python

from setuptools import setup

setup(
    name="nfq-conductor",
    description="NFQ Solutions tool for orchestration",
    version="0.3",
    author="NFQ Solutions",
    author_email="solutions@nfq.es",
    packages=[
        'nfq',
        'nfq.conductor'
        ],
    zip_safe=False,
    install_requires=['nfq', 'psutil', 'zmq', 'tornado', 'sqlalchemy'],
    include_package_data=True,
    setup_requires=[],
    tests_require=[],
    entry_points={
        'console_scripts': [
            'nfq-conductor=nfq.conductor.server:run',
            'nfq-conductor-daemon=nfq.conductor.daemon:run',
            'nfq-conductor-submit=nfq.conductor.submit:run']
        }
    )
