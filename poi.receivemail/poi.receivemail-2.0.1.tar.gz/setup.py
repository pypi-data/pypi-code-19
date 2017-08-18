from setuptools import setup, find_packages

version = '2.0.1'

setup(
    name='poi.receivemail',
    version=version,
    description="Receive email in the Poi issue tracker",
    long_description=(open("README.rst").read().strip() + "\n\n" +
                      open("CHANGES.rst").read().strip()),
    # Get more strings from
    # https://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Plone :: 3.2",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Plone :: 4.2",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.4",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    keywords='poi issue tracker mail',
    author='Maurits van Rees',
    author_email='maurits@vanrees.org',
    url='https://github.com/collective/poi.receivemail',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['poi'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'setuptools',
    ],
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
)
