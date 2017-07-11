from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(
    name='clipper-python',
    version='0.0.0',
    py_modules=['clipper_python'],
    
    author='Colin Palmer',
    author_email='colin.palmer@stfc.ac.uk',
    description='Python wrapper for the Clipper crystallographic library',
    long_description=readme(),
    url='http://www.ysbl.york.ac.uk/~cowtan/clipper/doc/',
    classifiers=[
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
