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
        name = 'pybuilder-smart-copy-resources',
        version = '0.1.6',
        description = 'PyBuilder plugin for copying additional resources',
        long_description = '\nPlease, see https://github.com/margru/pybuilder-smart-copy-resources for more information.\n',
        author = 'Martin Gruber',
        author_email = 'martin.gruber@email.cz',
        license = 'MIT',
        url = 'https://github.com/margru/pybuilder-smart-copy-resources',
        scripts = [],
        packages = ['pybuilder_smart_copy_resources'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 2.7'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
