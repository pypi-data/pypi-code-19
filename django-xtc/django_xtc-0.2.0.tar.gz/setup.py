from setuptools import setup

install_requires = [
    'Django>=1.9',
]

setup(
    install_requires=install_requires,
    extras_require={
        'docs': ['sphinx>=1.6'],
        'rtd': ['sphinx>=1.6', 'sphinx_rtd_theme'],
        'contributor': ['coverage>=4.4.1', 'sphinx>=1.6', 'twine']
    },
)
