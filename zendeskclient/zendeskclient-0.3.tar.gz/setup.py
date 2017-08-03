from distutils.core import setup

VERSION = '0.3'

setup(
    name='zendeskclient',
    packages=['zendeskclient'],
    version=VERSION,
    description='A Python ZenDesk client.',
    author='Taylor J. Meek, CloudBolt Software',
    author_email='taylor+pypi@cloudbolt.io',
    url='https://github.com/CloudBoltSoftware/zendeskclient',
    download_url='https://github.com/CloudBoltSoftware/zendeskclient/tarball/{version}'.format(version=VERSION),
    keywords=['zendesk', 'api', 'rest', 'client'],
    license='MIT',
    long_description=open('README').read(),
    classifiers=[],
    py_modules=['zendeskclient'],
)
