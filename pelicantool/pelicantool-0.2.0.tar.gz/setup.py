from setuptools import setup

with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

packages = ['pelicantool']
test_requirements = ['pytest>=3.1.2', 'pytest-cov']

entry_points = {
    'console_scripts': [
        'pelicantool = pelicantool.pelicantool:main',
    ]
}

setup(
    name='pelicantool',
    keywords='pelican auto tool',
    version='0.2.0',
    description='pelican auto tool',
    long_description=readme,
    author='Luo Xiaojie',
    author_email='xiaojieluoff@gmail.com',
    url='https://github.com/xiaojieluo/pelicantool',
    license=license,
    packages=packages,
    tests_require=test_requirements,
    classifiers=(
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy'
    ),
    test_suite='tests',
    entry_points=entry_points,

    python_requires='>=3',
)
