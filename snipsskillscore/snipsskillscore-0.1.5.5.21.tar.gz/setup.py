from setuptools import setup

setup(
    name='snipsskillscore',
    version='0.1.5.5.21',
    description='The Snips skills core utilities for creating end-to-end assistants',
    author='Michael Fester',
    author_email='michael.fester@gmail.com',
    url='https://github.com/snipsco/snips-skills-core',
    download_url='',
    license='MIT',
    install_requires=[
        'webrtcvad',
        'cython',
        'hidapi',
        'paho-mqtt',
        'pyyaml',
        'pyaudio',
        'pygame',
        'pyusb',
        'snips-respeaker',
        'gTTS'
    ],
    test_suite="tests",
    keywords=['snips'],
    packages=[
        'snipsskillscore'
    ],
    include_package_data=True,
)
