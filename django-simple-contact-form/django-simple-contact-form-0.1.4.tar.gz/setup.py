# coding=utf-8
import os

from setuptools import setup

setup(
    name='django-simple-contact-form',
    version='0.1.4',
    zip_safe=False,
    description='Generic contact-form application for Django',
    author='Evgeny Barbashov',
    author_email='evgenybarbashov@yandex.ru',
    url='https://github.com/bzzzzzz/django-simple-contact-form',
    packages=['contact_form', 'contact_form.tests'],
    long_description=open(os.path.join(os.path.dirname(__file__),
                          'README.rst')).read(),
    package_data={
        'contact_form': [
            'tests/templates/*/*.*',
            'locale/*/LC_MESSAGES/*.po',
        ]
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Utilities'
    ],
    install_requires=[
        'django>=1.8',
    ],
)
