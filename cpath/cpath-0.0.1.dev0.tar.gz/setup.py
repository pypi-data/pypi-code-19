from setuptools import setup, find_packages
import re
import ast

_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('cpath/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(name='cpath',
      version=version,
      description='Package with pathways utilities',
      url='https://github.com/Cristian-pg/cpath',
      author='Cristian Perez',
      author_email='Vilero89@gmail.com',
      license='GNU General Public License v3.0',
      packages=find_packages(),
      zip_safe=False,
      python_requires='>=3',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
      ],
      install_requires=[],
      )
