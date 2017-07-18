from setuptools import setup, find_packages

setup(name='docker-buildtool',
      version='0.0.19',
      url='http://github.com/openai/docker-buildtool',
      packages=[package for package in find_packages()
                if package.startswith('docker_buildtool')],
      scripts=['bin/docker-buildtool'],
      install_requires=['glob2', 'six', 'PyYAML', 'pathlib'],
)
