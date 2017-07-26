"""
Flask-BITSON-SQLAlchemy-Model
-----------------------------

BITSON's SQLALchemy Abstracts Model.
"""
from distutils.core import setup

setup(
    name='flask_btsn_alchemy',
    version='0.0.1',
    packages=['flask_btsn_alchemy'],
    url='https://gitlab.bitson.com.ar/lecovi/flask_btsn_alchemy.git',
    license='AGPL',
    author='Leandro E. Colombo Viña',
    author_email='colomboleandro@bitson.com.ar',
    description="BITSON's SQLAlchemy Models",
    long_description=__doc__,
    # zip_safe=False,
    # include_package_data=True,
    platforms='any',
    # install_requires=[
    #     'Flask',
    #     'Flask-SQLAlchemy',
    #     'rainbow_logging_handler'
    # ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]

)
