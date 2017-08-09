from setuptools import setup, find_packages

setup(
    # Metadata
    name='thelab-gauth',
    version='0.1.1',
    description='Mostly drop in django app to use Google Apps for thelab users.',
    packages=['labgauth'],
    url='https://gitlab.com/thelabnyc/thelab-gauth',
    include_package_data=True,
    license="Apache License",
    author_email="dburke@thelabnyc.com",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # Dependencies
    install_requires=[
        'Django>=1.9.6',
        'django-allauth>=0.32.0',
    ],

)
