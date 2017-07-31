from setuptools import setup

setup(
    name='snipsskillscore',
    version='0.1.5',
    description='The Snips skills core utilities for creating end-to-end assistants',
    author='Michael Fester',
    author_email='michael.fester@gmail.com',
    url='https://github.com/snipsco/snips-skills-core',
    download_url='',
    license='MIT',
    install_requires=[
        'enum',
        'paho-mqtt',
        'pyyaml',
        'pyaudio',
        'pygame'
    ],
    test_suite="tests",
    keywords=['snips'],
    packages=[
        'snipsskillscore'
    ]
)
