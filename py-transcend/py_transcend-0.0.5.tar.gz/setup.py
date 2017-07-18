# Compile package: python setup.py sdist
# Install package: pip install .
# Publish package: python setup.py sdist upload



from setuptools import setup
 
setup(
    name='py_transcend',   
    version='0.0.5',                       
    description= 'Python utilties for managing Transcend data.',
    author='Michael Farrell',
    author_email='mike@transcendbeta.com',
    packages = ['transcend', 'transcend/services'],
    # Choose your license
    license='MIT',
    url='https://github.com/transcend-inc/py-transcend',
)