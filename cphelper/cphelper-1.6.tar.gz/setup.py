from distutils.core import setup

setup(
    name = 'cphelper',
    packages = ['cphelper'],
    package_dir={'cphelper':'cphelper'},
    package_data={'cphelper':['management/commands/*', 'migrations/*']},
    version = '1.6',
    description = 'A API which will return Course of specific Dept. and also Course which you can enroll at that time.',
    author = 'davidtnfsh',
    author_email = 'davidtnfsh@gmail.com',
    url = 'https://github.com/Stufinite/cphelper',
    download_url = 'https://github.com/Stufinite/cphelper/archive/v1.6.tar.gz',
    keywords = ['coursepickinghelper', 'timetable', 'campass'],
    classifiers = [],
    license='GNU3.0',
    install_requires=[
        'djangoApiDec',
        'pymongo==3.4.0',
    ],
    zip_safe=True
)
