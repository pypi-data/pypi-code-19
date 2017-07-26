from distutils.core import setup

VERSION = "0.0.1"

setup(
    name='sc2trainingassistant',
    packages=['trainingassistantreplaywatcher'],
    version=VERSION,
    description='Replay handler for an sc2 macro training assistant',
    author='Hugo Wainwright',
    author_email='wainwrighthugo@gmail.com',
    url='https://github.com/frugs/sc2trainingassistant',
    download_url='https://github.com/frugs/sc2trainingassistant/tarball/' + VERSION,
    keywords=['sc2', 'replay', 'macro', 'training'],
    license='MIT',
    install_requires=['sc2replaynotifier', 'aiohttp'],
    classifiers=[],
)
