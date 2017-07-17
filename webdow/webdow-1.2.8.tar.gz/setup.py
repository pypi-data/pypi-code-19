from distutils.core import setup

setup(
    name = 'webdow',
    packages = ['webdow'],
    version = '1.2.8',
    license="GPL-3.0",
    description = 'A python pacakge to download htmlSource for a webpage, even when the webpage is dynamically loading.',
    author = 'Arvindsinc2',
    author_email = 'arvindsinc2@hotmail.com',
    url = 'https://github.com/Arvindsinc2/webdow',
    download_url = 'https://github.com/Arvindsinc2/webdow/archive/1.2.0.tar.gz',
    keywords = ['python', 'html','downloader','dynamic','dynamically','loading','webpage','ajax','save'],
    classifiers = [],
    install_requires=[
        'pyvirtualdisplay',
        'selenium'
    ],
)