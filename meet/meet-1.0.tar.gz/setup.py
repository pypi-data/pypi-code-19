from setuptools import setup, find_packages


setup(
    name='meet',
    version='1.0',
    author='Jeffrey B. Daube',
    author_email='daubejb@gmail.com',
    packages=find_packages(),
    licenses='MIT license',
    include_package_data=True,
    zip_safe=False,
    url="http://www.github.com/daubejb/meet",
    download_url='https://github.com/daubejb/meet/archive/0.1/tar/gz',
    description='A simple cli utility to create a meeting notes document in \
    either a google doc on google drive or in markdown in your directory of \
    choice',
    keywords='meeting notes generator google docs markdown daube design',
    install_requires=[
        'googleapiclient',
        'oauth2client',
        'google-api-python-client',
        ],
    entry_points={
        'console_scripts': [
            'meet=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Programming Language :: Python :: 3.5',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Communications',
        'Topic :: Terminals',
        'Topic :: Office/Business',
        'Topic :: Utilities'
        ],
    )
