from setuptools import setup

setup(
    name = 's3df',
    packages = ['s3df'],
    version = '0.0.1',
    description = 'Pandas DataFrame wrapper to create DataFrame from file on S3',
    author = 'Junya Kaneko',
    author_email = 'jyuneko@hotmail.com',
    url = 'https://github.com/JunyaKaneko/pys3df',
    download_url = 'https://github.com/JunyaKaneko/pys3df.git',
    keywords = ['s3', ],
    license='MIT',
    install_requires = ['pandas', 's3client'],
    classifiers = [],
)
