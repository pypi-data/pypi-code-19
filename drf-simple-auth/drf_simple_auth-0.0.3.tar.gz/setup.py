from setuptools import setup

DESCRIPTION = "Simple login/signup APIs using Django Rest Framework."


setup(
    name="drf_simple_auth",
    version="0.0.3",
    url='https://github.com/nickromano/drf-simple-auth',
    license='BSD',
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author='Nick Romano',
    author_email='nick.r.romano@gmail.com',
    packages=['drf_simple_auth', 'drf_simple_auth.migrations'],
    install_requires=[
        'Django>=1.8,<=1.11.3',
        'djangorestframework>=3.6.3',
    ],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    tests_require=[
    ],
    test_suite='testrunner.runtests'
)
