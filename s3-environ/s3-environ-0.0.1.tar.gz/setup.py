import os
from setuptools import setup


with open(os.path.join(os.path.dirname(__file__), 'requirements.txt')) as f:
    required = f.read().splitlines()

with open(os.path.join(os.path.dirname(__file__), 'requirements_test.txt')) as f:
    test_required = f.read().splitlines()


setup(
    author='Jonatas Baldin',
    author_email='jonatas.baldin@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    description='Load environment variables from a AWS S3 file!',
    license='MIT License',
    url='https://github.com/jonatasbaldin/s3-environ',
    include_package_data=True,
    install_requires=required,
    tests_require=test_required,
    name='s3-environ',
    packages=['s3-environ'],
    version='0.0.1'
)
