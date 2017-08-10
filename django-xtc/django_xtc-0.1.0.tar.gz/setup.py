from setuptools import setup

install_requires = [
    'Django>=1.9',
]

setup(
    install_requires=install_requires,
    extras_require={
        'docs': ['sphinx>=1.6'],
    },
)
