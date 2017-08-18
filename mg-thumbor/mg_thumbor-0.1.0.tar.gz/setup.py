from setuptools import setup

setup(name='mg_thumbor',
    version='0.1.0',
    description='Extra filters and optimizers for thumbor by MindGeek',
    url='https://github.com/MindGeekOSS/mg_thumbor',
    author='Fabrice Baumann',
    author_email='fabrice.baumann@mindgeek.com',
    license='MIT',
    packages=['mg_thumbor', 'mg_thumbor.filters'],
    zip_safe=False,
    install_requires=[
        'thumbor',
    ]
)
