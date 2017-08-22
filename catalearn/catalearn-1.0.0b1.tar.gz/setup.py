from setuptools import setup, find_packages

setup(
    name='catalearn',
    version='1.0.0b1',
    description='A module for running machine learning code on cloud GPUs',
    url='https://github.com/Catalearn/catalearn',
    author='Edward Liu',
    author_email='edward@catalearn.com',
    license='MIT',
    keywords='machinelearning gpu cloud',
    packages=find_packages(exclude=['contrib', 'docs', 'tests']),
    install_requires=[
        'dill',
        'requests',
        'websocket-client',
        'requests_toolbelt',
        'Ipython',
        'tqdm'
    ],
    python_requires='>=3'
)
