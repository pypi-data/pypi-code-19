from setuptools import setup, find_packages

setup(
    name='bigparser',
    version='0.0.9',
    url='https://github.com/ajayarjun-bka/bigparser-python-lib',
    author='Ajay Arjun',
    author_email='arjun.bka@gmail.com',
    description='Python client library for BigParser\'s API to fetch data from grids.',
    packages=find_packages(exclude=['tests','app.py']),
    zip_safe=False,
    include_package_data=True,
    license='MIT',
    python_requires=">=3.1",
    install_requires=[
        'requests', 'pandas', 'numpy'
    ],
)
