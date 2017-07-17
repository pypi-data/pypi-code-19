from setuptools import setup, find_packages

setup(
    name='mit',
    version='0.0.3',
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=[
        'click==6.7',
        'colorama==0.3.9',
        'enum34==1.1.6',
        'GitPython==2.1.5'
    ],
    entry_points={
        'console_scripts': [
            'mit = mit:cli',
        ],
    },
)
