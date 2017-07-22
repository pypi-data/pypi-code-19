from distutils.core import setup

from setuptools.command.install import install


class PostInstallCommand(install):
    def run(self):
        import sveder
        install.run(self)


setup(
    name = 'sveder',
    packages = ['sveder'],
    version = '0.4',
    description = 'Visit sveder.com :)',
    author = 'Sveder',
    author_email = 'm@sveder.com',
    url = 'https://github.com/Sveder/import-sveder',
    download_url = 'https://github.com/Sveder/import-sveder/archive/0.1.tar.gz',
    keywords = ['sveder', 'shameless', 'self', 'promotion'],
    cmdclass={
        'install': PostInstallCommand,
    },
)