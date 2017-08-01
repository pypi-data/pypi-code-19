import setuptools


with open('README.rst') as f:
    readme = f.read()


setuptools.setup(
    name='python-scripting',
    version='0.1.0',
    description='Boilerplate for Python scripting',
    long_description=readme,
    author='Noah Green',
    author_email='noahc.green@icloud.com',
    url='https://github.com/noahcgreen/python-scripting',
    license='MIT',
    packages=['scripting', 'scripting._terminal'],
    include_package_data=True,
    setup_requires=['pytest-runner', 'pytest-catchlog'],
    tests_require=['pytest'],
    python_requires='~=3.6'
)
