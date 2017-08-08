from setuptools import setup


def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='adxl345',
    version='1.0.4',
    description='Python module to use ADXL345.',
    long_description=readme(),
    url='https://github.com/alcalyn/adxl345',
    author='Alcalyn',
    author_email='doubjulien@hotmail.fr',
    license='MIT',
    packages=[
        'adxl345',
    ],
    use_2to3=True,
    zip_safe=False,
)
