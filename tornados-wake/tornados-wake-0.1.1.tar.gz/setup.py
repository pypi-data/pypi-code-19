"""
`GitHub <https://github.com/jonmcoe/tornados-wake>`_.
"""
from setuptools import setup


setup(
    name="tornados-wake",
    version="0.1.1",
    author="Jon Coe",
    author_email="jonmcoe@gmail.com",
    description="Tornado's Wake: Handler and tools for inspecting routes of a tornado server",
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3'
    ],
    # license="XXX",  # TODO: choose license
    keywords="tornado tornadoweb routes handlers index",
    url="https://github.com/jonmcoe/tornados-wake",
    packages=['tornados_wake'],
    long_description=__doc__,
    install_requires=['tornado>=3'],
    tests_require=['nose']
)
