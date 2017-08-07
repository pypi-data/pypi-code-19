from setuptools import setup, find_packages

setup(
    name='chall-cube',
    version='1.0.3',
    description='Base API for RaspberryPi challenges cube.',
    url='http://github.com/alcalyn/chall-cube',
    author='Alcalyn',
    author_email='doubjulien@hotmail.fr',
    license='AGPL-3.0',
    packages=find_packages('.'),
    install_requires=[
        'gpiocrust>=1.0.0',
    ],
    zip_safe=False
)
