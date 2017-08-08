from distutils.core import setup

setup(
    name = 'curso',
    packages = ['curso'],
    version = '1.6',
    description = 'A search Engine that use KCM & KEM api invented by UDIC at NCHU.',
    author = 'davidtnfsh',
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/Stufinite/curso',
    download_url = 'https://github.com/Stufinite/curso/archive/v1.6.tar.gz',
    keywords = ['Search Engine', 'campass'],
    classifiers = [],
    license='MIT',
    install_requires=[
        'djangoApiDec',
        'jieba==0.38',
        'pymongo==3.4.0',
        'PyPrind==2.9.9',
        'requests==2.12.3',
        'simplejson==3.10.0',
    ],
    zip_safe=True
)
