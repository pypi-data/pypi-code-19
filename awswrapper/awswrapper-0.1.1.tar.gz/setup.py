import setuptools

try:
    with open('README.md') as f:
        long_description = f.read()
except IOError:
    long_description = ""

requirements = ['boto3']

setuptools.setup(
    name='awswrapper',
    license='MIT',
    author='Hector Reyes Aleman',
    author_email='birkoffh@gmail.com',
    install_requires=requirements,
    version='0.1.1',
    packages=['awswrapper'],
    description='Wrapper of AWS API to use with Lambda',
    long_description=long_description,
    url='https://github.com/birkoff/PythonAwsWrapper'
)
