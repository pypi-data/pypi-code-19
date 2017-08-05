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
        name = 'yumrepos',
        version = '0.9.9',
        description = 'yumrepos: simple yum repositories with minimal rest api',
        long_description = 'yumrepos\n- serve yum repositories as simple folders\n- ... via web server\n- offer rest api for\n   - create/remove/link of repositories\n   - upload/stage/remove of rpms\n',
        author = 'Arne Hilmann',
        author_email = 'arne.hilmann@gmail.com',
        license = '',
        url = 'https://github.com/arnehilmann/yumrepos',
        scripts = ['scripts/yumrepos'],
        packages = [
            'yumrepos',
            'yumrepos.backports'
        ],
        namespace_packages = [],
        py_modules = ['braceexpand'],
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'flask',
            'werkzeug'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
