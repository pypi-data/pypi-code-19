from setuptools import setup

setup(
    name='recoo',
    version='0.1',
    description='Command line api for taste dive.',
    author='Kalpesh Adhatrao',
    author_email='kalpesh.adhatrao@gmail.com',
    license='MIT',
    packages=['recoo'],
    install_requires=[
        'Click', 'requests', 'clr', 'terminaltables'
    ],
    entry_points='''
        [console_scripts]
        recoo=recoo:cli
    ''',
    zip_safe=False
)
