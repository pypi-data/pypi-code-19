from setuptools import setup


setup(
    name='goroutine',
    version='0.0.1',
    py_modules=['goroutine'],
    install_requires=['greenlet'],
    url='http://github.com/rokups/goroutine',
    description='Use greenlets as coroutines in asyncio',
    keywords=['greenlet', 'coroutine', 'asyncio'],
    license='MIT',
)
