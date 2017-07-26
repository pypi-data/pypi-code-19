from setuptools import setup

VERSION = "0.0.1"

setup(
    name='trainingassistantclient',
    packages=['trainingassistantclient'],
    version=VERSION,
    author='Hugo Wainwright',
    author_email='wainwrighthugo@gmail.com',
    keywords=['sc2', 'replay', 'macro', 'training'],
    license='MIT',
    install_requires=['sc2trainingassistant', 'sc2replaynotifier'],
    classifiers=[],
    entry_points={
        'console_scripts': ['training-assistant=trainingassistantclient.trainingassistant:main'],
    }
)
