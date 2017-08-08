from os import path
from setuptools import setup


def read(fname):
    return open(path.join(path.dirname(__file__), fname)).read()

setup(
    name='django-static-md5url',
    version='0.1',
    description='Versioning django static files in production. Add md5 suffix to url',
    author='Saladraj Eugene',
    author_email='saladrai@gmail.com',
    url='https://github.com/saladrai/django-static-md5url',
    packages=['django_static_md5url'],
    include_package_data=True,
    zip_safe=False,
    long_description=read('README.md'),
    license='MIT',
    keywords='django static md5url',
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
