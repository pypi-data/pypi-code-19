import os
from setuptools import find_packages, setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='rijndael',
    version='0.1.0',
    packages=find_packages(),
    test_suite='rijndael.tests',
    include_package_data=True,
    author='Moeen Zamani',
    author_email='moeen.zamani@gmail.com',
    license='MIT',
    description='Rijndael AES encryption algorithm in pure python.',
    url='https://github.com/moeenz/rijndael',
    classifiers=[
        'Environment :: Console',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: Unix',
        'Programming Language :: Python'
    ],
)
