#!/usr/bin/env python
from setuptools import setup
from setuptools.command.test import test as BaseTestCommand
from djangocms_local_navigation import __version__


install_requires = [
    'django-cms>=3.0',
    'beautifulsoup4',
]

tests_require = [
    'djangocms-text-ckeditor',
]


class TestCommand(BaseTestCommand):
    def run_tests(self):
        import sys
        import django
        from django.conf import settings
        from django.test.runner import DiscoverRunner

        from tests import settings as test_settings

        settings.configure(**{
            setting: getattr(test_settings, setting)
            for setting in dir(test_settings)
            if setting.isupper()
        })

        django.setup()
        test_runner = DiscoverRunner(verbosity=1)

        failures = test_runner.run_tests(['tests'])
        if failures:
            sys.exit(failures)


setup(
    name='djangocms-local-navigation',
    version=__version__,
    packages=['djangocms_local_navigation'],
    author='Sylvain Fankhauser',
    author_email='sylvain.fankhauser@liip.ch',
    description="Display menus based on the HTML structure of the pages",
    long_description=open('README.md').read(),
    url='https://github.com/liip/djangocms-local-navigation',
    install_requires=install_requires,
    tests_require=tests_require,
    license='BSD',
    include_package_data=True,
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    cmdclass={
        'test': TestCommand,
    }
)
