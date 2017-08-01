from setuptools import setup

setup(
    name='npack',
    packages=['npack'],  # this must be the same as the name above
    version='0.3.4',
    description='Netflix Packager for ContentHub',
    license='MIT',
    author='Anton Margoline',
    author_email='amargoline@netflix.com',
    url='https://contenthub.netflix.com/projects',
    download_url='https://drive.google.com/open?id=0B-J_HAq02T2venZadjRXcDVfajg',
    keywords=[],
    classifiers=[],
    entry_points={
        'console_scripts': [
            'npack = npack.__main__:main'
        ]
    },
)