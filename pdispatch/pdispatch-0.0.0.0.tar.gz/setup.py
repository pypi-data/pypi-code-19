from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='pdispatch',
    version='0.0.0.0',
    license='MIT',
    description='A small ad hoc plugin applicator and binder for Python 3.',
    long_description=long_description,
    author='Srishan Bhattarai',
    author_email='srishanbhattarai@gmail.com',
    url='https://github.com/srishanbhattarai/pdispatch',
    packages=['pdispatch'],
    install_requires=[
    ],
    include_package_data=True,
    classifiers=[
        'Operating System :: MacOS :: MacOS X',
    ]
)
