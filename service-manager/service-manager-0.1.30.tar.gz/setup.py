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
        name = 'service-manager',
        version = '0.1.30',
        description = 'CLI for managing micro-services',
        long_description = 'CLI for managing micro-services',
        author = '',
        author_email = '',
        license = 'Apache 2.0',
        url = 'https://github.com/AlienVault-Engineering/service-manager',
        scripts = ['scripts/service-manager'],
        packages = [
            'service_manager',
            'service_manager.service_initializer',
            'service_manager.util',
            'service_manager.vcs',
            'service_manager.service_initializer.creators'
        ],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {
            'service_manager': ['service_initializer/creators/builtin_service_templates.json']
        },
        install_requires = [
            'cookiecutter',
            'pybitbucket'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
