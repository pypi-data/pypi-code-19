from setuptools import setup


setup(
    name='autocomplete_widget',
    version=__import__('autocomplete_widget').__version__,
    url='https://www.rug.nl/rus/cit/',
    author='Research and Innovation Support',
    author_email='H.T.Kruitbosch@rug.nl',
    description=('A widget that autocompletes (without ajax)'),
    packages=[
        'autocomplete_widget'
    ],
    include_package_data=True,
    install_requires=['django'],
    extras_require={},
    zip_safe=False,
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
