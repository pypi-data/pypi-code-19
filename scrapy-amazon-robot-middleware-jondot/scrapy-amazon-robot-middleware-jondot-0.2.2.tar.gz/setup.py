from setuptools import setup, find_packages

version = '0.2.2'

REQUIREMENTS = ['beautifulsoup4', 'scrapy', 'pillow==4.0.0', 'requests']

setup(
    name='scrapy-amazon-robot-middleware-jondot',
    version=version,
    packages=find_packages(),
    package_data={'captchabuster': ['iconset/**/*.gif']},
    url='https://github.com/leon-wu/scrapy-amazon-robot-middleware',
    license='LICENSE.txt',
    author='Mark Sanders',
    author_email='xmwlzhi@gmail.com',
    install_requires=REQUIREMENTS,
    description='Scrapy middleware module which uses image parsing to submit a captcha response to amazon.',
    include_package_data=True)
