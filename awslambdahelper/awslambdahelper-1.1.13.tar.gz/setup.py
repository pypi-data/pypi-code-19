#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'awslambdahelper',
        version = '1.1.13',
        description = '',
        long_description = '',
        author = 'Drew J. Sonne',
        author_email = 'drew.sonne@gmail.com',
        license = 'LGLP',
        url = 'http://lambda.awshelpers.com/',
        scripts = ['scripts/lambdahelper-bundler'],
        packages = ['awslambdahelper'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'backoff',
            'boto3',
            'pip>=7.1',
            'setuptools~=35.0'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
