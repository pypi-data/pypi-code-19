from distutils.core import setup
setup(
    name='public_health_cis',
    packages=['public_health_cis'], # this must be the same as the name above
    py_modules=['public_health_cis'],
    version='0.1.3',
    description='A lib to calculate specific confidence intervals that are used in Public Health',
    author='Russell Plunkett',
    author_email='russ.plunkett@gmail.com',
    url='https://github.com/RustyBrain/PublicHealthCIs.git', # use the URL to the github repo
    download_url='https://github.com/RustyBrain/PublicHealthCIs/archive/0.1.2.tar.gz', # I'll explain this in a second
    keywords=['confidence interval', 'wilsons', 'byars', 'statistics'], # arbitrary keywords
    classifiers=[
        'Programming Language :: Python :: 3',
        'Topic :: Scientific/Engineering :: Mathematics',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Education',
    ],
)
