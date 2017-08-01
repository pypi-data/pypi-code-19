from setuptools import setup

setup(
    name='snipslocalmusic',
    version='0.1.0.4',
    description='Local music player skill for Snips',
    author='Michael Fester',
    author_email='michael.fester@gmail.com',
    url='https://github.com/snipsco/snips-skill-localmusic',
    download_url='',
    license='MIT',
    install_requires=['pygame'],
    test_suite="tests",
    keywords=['snips'],
    include_package_data=True,
    packages=[
        'snipslocalmusic'
    ]
)
