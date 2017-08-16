from setuptools import setup, find_packages

setup(
    name='digimat.logserver',
    version='0.1.1',
    description='Digimat TCP Python Logging Server',
    namespace_packages=['digimat'],
    author='Frederic Hess',
    author_email='fhess@st-sa.ch',
    url='http://www.digimat.ch',
    license='PSF',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=[
        'setuptools'
    ],
    dependency_links=[
        ''
    ],
    zip_safe=False)
