from setuptools import setup, find_packages

setup(
    name = 'get-back-to-work-ronald',
    packages = find_packages(),
    version = '0.1',
    description = 'Tell Ronald to get back to work',
    author = 'Jonathan Boudreau',
    author_email = 'jonathan.boudreau.92@gmail.com',
    url = 'https://github.com/AGhost-7/get-back-to-work-ronald',
    download_url = '',
    keywords = ['joke'],
    classifiers = [],
    install_requires = [
        'flask'
    ],
    entry_points = { 
        'console_scripts': [
            'get-back-to-work-ronald=get_back_to_work_ronald:main'
        ]
    }
)
