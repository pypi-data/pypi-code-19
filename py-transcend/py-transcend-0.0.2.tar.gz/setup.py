# Compile package: python setup.py sdist
# Install package: pip install .
# Publish package: python setup.py register sdist upload -r https://www.python.org/pypi


from setuptools import setup
 
setup(
    name='py-transcend',   
    version='0.0.2',                       
    description= 'Python utilties for managing Transcend data.',
    author='Michael Farrell',
    author_email='mike@transcendbeta.com',
    packages = ['transcend', 'transcend/services'],
    # Choose your license
    license='MIT',
    url='https://github.com/transcend-inc/py-transcend',
)