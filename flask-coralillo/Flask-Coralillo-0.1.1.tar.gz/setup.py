from setuptools import setup, find_packages


setup(
    name='Flask-Coralillo',
    version='0.1.1',
    url='http://categulario.github.io/flask_coralillo',
    license='MIT',
    author='Abraham Toriz Cruz',
    author_email='categulario@gmail.com',
    description='Flask module for the Coralillo redis ORM',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'coralillo',
    ],
    test_suite = 'flask_coralillo.tests.test_flask_coralillo',
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
