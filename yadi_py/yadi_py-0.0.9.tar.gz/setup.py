import os
from setuptools import setup, find_packages
from setuptools.command.install import install
from yadi import binary, version

PKG_NAME = 'yadi'

class PostInstallCommand(install):
    def run(self):
        install.run(self)
        dest = os.path.join(self.install_purelib, PKG_NAME, 'vendor', binary.dest())
        print('Download Yadi to: %s' % dest)
        self.download(dest)


    def download(self, dst):
        try:
            # Python 3
            from urllib.request import urlretrieve
        except ImportError as e:
            # Python 2
            from urllib import urlretrieve
        download_uri = binary.uri(version.LATEST)
        try:
            urlretrieve(download_uri, dst)
        except Exception as e:
            raise Exception('Failed to download yadi from url %s: %s' % (download_uri, e))
        os.chmod(dst, 0o755)


setup(
    name='yadi_py',
    version=version.LATEST,
    description='Yadi wrapper that makes it seamlessly available as a local dependency',
    author='Yandex IS Team',
    author_email='buglloc@yandex-team.ru',
    url='https://github.yandex-team.ru/product-security/yadi',
    entry_points={
        'console_scripts': ['yadi=yadi.main:main'],
    },
    packages=[PKG_NAME],
    package_data={PKG_NAME: ['vendor/readme.txt']},
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Security',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing'
    ],
    cmdclass={
        'install': PostInstallCommand,
    },
    )
