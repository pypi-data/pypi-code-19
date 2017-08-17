from setuptools import setup
setup(
    author='Kieran O\'Leary',
    author_email='kieran.o.leary@gmail.com',
    description='Insert chapter markers for scene changes using Matroska using ffmpeg and mkvpropedit',
    entry_points={
        'console_scripts': [
            'scenechange=scenechange.scenechange:main',
        ],
    },
    license='MIT',
    name='scenechange',
    version='0.8'
)