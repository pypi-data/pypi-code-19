from distutils.core import setup

setup(
    name='pewsql',
    version='0.0.1',
    packages=['pewsql'],
    url='',
    license='',
    classifiers=[
        "Intended Audience :: Science/Research",
        "Intended Audience :: System Administrators",
        "Topic :: Database",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Information Analysis"
    ],
    install_requires=['pony', 'pandas', 'numpy', 'psycopg2'],
    python_requires='>=3',
    author='anderson',
    author_email='a141890@gmail.com',
    description='Analytics Tools for RDBMS',
    keywords=['sql', 'analytics']
)
