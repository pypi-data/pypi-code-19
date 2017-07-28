from distutils.core import setup

setup(
    name='sciblox',
    version='0.2.9',
    author='Daniel Han-Chen',
    author_email='danielhanchen@gmail.com',
    packages=['sciblox'],
    url='https://github.com/danielhanchen/sciblox',
    download_url = 'https://github.com/danielhanchen/sciblox/sciblox-0.2.8.tar.gz',
    keywords = ['data science', 'data analytics', 'machine learning',
    'data visualisation', 'MICE', 'imputation', 'BPCA', 'CARET',
    'data analytics'],
    license='LICENSE.txt',
    description='Making data science and machine learning in Python easier.',
    long_description=open('README.txt').read(),
    install_requires=[
        "scikit-learn >= 0.18.0",
        "pandas >= 0.18.1",
        "scipy >= 0.19.0",
        "matplotlib >= 2.0.0",
        "seaborn >= 0.8.0",
        "lightgbm >= 2.0.0",
        "jupyter >= 0.9.0",
        "numpy >= 1.12.1"
    ],
    extras_require = {
        'theano':  ["theano >= 0.8.0"],
        'fancyimpute': ["fancyimpute >= 0.2.0"],
        'sympy': ["sympy >= 1.1.0"],
        'jupyterthemes': ["jupyterthemes >= 0.16.0"]
    }
)
