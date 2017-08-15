from setuptools import setup

license = open('LICENSE.txt').read()

setup(
    name='iloveig',
    version='0.0.2',
    author='xwaynec',
    author_email='xwaynec@gmail.com',
    packages=['iloveig'],
    url='https://github.com/xwaynec/iloveig',
    license=license,
    description='Download images from instagram',
    test_suite='tests',
    long_description=open('README.md').read(),
    entry_points = {
        'console_scripts': [
            'iloveig = iloveig.iloveig:main',
        ]
    },
    install_requires = [
        "beautifulsoup4==4.6.0",
        "certifi==2017.7.27.1",
        "chardet==3.0.4",
        "idna==2.5",
        "requests==2.18.3",
        "urllib3==1.22",
    ],
)
