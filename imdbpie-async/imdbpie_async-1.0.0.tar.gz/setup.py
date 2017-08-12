from setuptools import setup

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

with open('README.md') as r:
    readme = r.read()

version = '1.0.0'
package_data = {'': ['LICENSE', 'requirements.txt', 'README.md', 'COPYING']}
setup(
    name='imdbpie_async',
    author='MaT1g3R',
    url='https://github.com/hifumibot/imdb-pie',
    version=version,
    license='MIT',
    description='An async fork to imdb-pie',
    install_requires=requirements,
    packages=['imdbpie_async'],
    long_description=readme,
    include_package_data=True,
    package_data=package_data
)
