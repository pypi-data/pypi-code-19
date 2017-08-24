import distutils.core


distutils.core.setup(
    name='pylint_extra',
    packages=['pylint_extra'],
    version='0.1.0',
    description='',
    author='Mat Lee',
    author_email='matt@lumidatum.com',
    url='https://www.lumidatum.com',
    download_url='',
    keywords=['pylint', 'zmq'],
    classifiers=[],
    install_requires=[
        'astroid',
    ]
)
