import setuptools 


try:
    with open('README.rst') as f:
        long_description = f.read()
except IOError:
    long_description = ""

requirements=['boto3']


setuptools.setup(
    name='awswrapper',
    license='MIT',
    author='Hector Reyes Aleman',
    author_email='birkoffh@gmail.com',
    install_requires=requirements,
    version='0.1.0',
    packages=['awswrapper'],
    description='Wrapper of AWS API',
    long_description=long_description
)
