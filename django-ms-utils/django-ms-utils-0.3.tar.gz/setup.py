from setuptools import setup, find_packages

f = open('README')
readme = f.read()
f.close()

setup(
    name='django-ms-utils',
    version='0.3',
    description='Django Master Soft utilities',
    long_description=readme,
    author='Master Soft s.r.l.',
    packages=find_packages(),
    package_data={
        'ms_utils': [
            'templates/ms_utils/*.html',
            'templates/ms_utils/menu/*.html',
            'templates/ms_utils/tags/*.html',
            'templates/ms_utils/widgets/*.html',
            'templates/ms_utils/form/*.html',
            'templates/ms_utils/form/widgets/*.html',
            'static/ms_utils/css/*.css',
            'static/ms_utils/css/skins/*.css',
            'static/ms_utils/fonts/*',
            'static/ms_utils/images/*',
            'static/ms_utils/js/*.js',
        ]
    },
    install_requires=[
        'django',
        'django-filter',
        'django-select2',
        'django-tables2',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
