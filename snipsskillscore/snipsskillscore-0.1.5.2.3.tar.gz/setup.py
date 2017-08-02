from setuptools import setup

setup(
    name='snipsskillscore',
    version='0.1.5.2.3',
    description='The Snips skills core utilities for creating end-to-end assistants',
    author='Michael Fester',
    author_email='michael.fester@gmail.com',
    url='https://github.com/snipsco/snips-skills-core',
    download_url='',
    license='MIT',
    install_requires=[
        'paho-mqtt',
        'pyyaml',
        'pyaudio',
        'pygame'
    ],
    dependency_links=[
        "hg+http://bitbucket.org/pygame/pygame"
    ],
    test_suite="tests",
    keywords=['snips'],
    packages=[
        'snipsskillscore'
    ]
)
