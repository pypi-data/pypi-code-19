from setuptools import setup

with open('README.md') as f:
    readme = f.read()

setup(
    version='0.1.3',
    name='EventableFuelSDK',
    description='ExactTarget Fuel SDK for Python, modified for Eventable',
    long_description=readme,
    author='Eventable',
    author_email='will@eventable.com',
    py_modules=['ET_Client'],
    packages=['EventableFuelSDK'],
    url='https://github.com/eventable/FuelSDK-Python',
    license='MIT',
    install_requires=[
        'pyjwt>=0.1.9',
        'requests>=2.2.1',
        'suds>=0.4',
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries',
        'Programming Language :: Python :: 2.7',
    ],
)
