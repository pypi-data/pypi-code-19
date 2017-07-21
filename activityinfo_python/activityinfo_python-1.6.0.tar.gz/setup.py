from distutils.core import setup

setup(
    name='activityinfo_python',
    version='1.6.0',
    author='James Cranwell-Ward',
    author_email='jcranwellward@unicef.org',
    py_modules=['activityinfo_client'],
    install_requires=['requests'],
    description='Simple python wrapper for ActivityInfo REST API',
    url='https://github.com/HCDX/ActivityInfoPython',
    download_url='https://github.com/HCDX/ActivityInfoPython/archive/v1.6.0.tar.gz',
    keywords=['activityinfo', 'api', 'requests', 'python'],
    classifiers = [],
)
