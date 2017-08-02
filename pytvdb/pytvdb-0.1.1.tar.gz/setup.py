from distutils.core import setup

requirements = [
    'certifi==2017.4.17',
    'chardet==3.0.4',
    'idna==2.5',
    'requests==2.18.1',
    'ttldict==0.3.0',
    'urllib3==1.21.1',
]

setup(
    name='pytvdb',
    version='0.1.1',
    packages=['pytvdb'],
    url='https://github.com/jwbaker/pytvdb',
    license='Unlicense',
    author='Jason Baker',
    author_email='bakerjwr@gmail.com',
    description='A library for connecting to the TVDB.com API',
    install_requires=requirements,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
)
