from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except(IOError, ImportError):
    long_description = open('README.md').read()

setup(
    author='Edward Anderson',
    author_email='edward.anderson@bfi.org.uk',
    description='Filters media files by testing criteria against header metadata extracted by ffprobe.',
    entry_points={
        'console_scripts': [
            'fffilter=fffilter.fffilter:main',
        ],
    },
    install_requires=[
      'colorama',
    ],
    license='Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)',
    long_description=long_description,
    name='FFfilter',
    packages=find_packages(),
    version='0.0.1'
)