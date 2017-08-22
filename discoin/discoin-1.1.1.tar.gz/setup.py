from setuptools import setup
import re, os

requirements = ['requests']

version = ''
with open('discoin/__init__.py') as f:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', f.read(), re.MULTILINE).group(1)

if not version:
    raise RuntimeError('version is not set')

readme = ''
with open('README') as f:
    readme = f.read()



setup(name='discoin',
      author='JoeBanks13',
      author_email="joseph@josephbanks.me",
      url='https://gitlab.josephbanks.me/JoeBanks13/discoin-python',
      version=version,
      packages=['discoin'],
      license='MIT',
      description='A python wrapper for Discoin API',
      long_description=readme,
      include_package_data=True,
      install_requires=requirements,
      classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
      ]
)
