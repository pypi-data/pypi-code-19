from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='adxl345',
    version='1.0.2',
    description='Python module to use ADXL345.',
    long_description=readme(),
    url='https://github.com/alcalyn/adxl345',
    author='Alcalyn',
    author_email='doubjulien@hotmail.fr',
    license='MIT',
    packages=find_packages('.'),
    zip_safe=False
)
