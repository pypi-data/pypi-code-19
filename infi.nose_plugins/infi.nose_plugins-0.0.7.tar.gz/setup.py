
SETUP_INFO = dict(
    name = 'infi.nose_plugins',
    version = '0.0.7',
    author = 'Arnon Yaari',
    author_email = 'arnony@infinidat.com',

    url = 'https://git.infinidat.com/host-opensource/infi.nose_plugins',
    license = 'BSD',
    description = """nose plugins""",
    long_description = """nose plugins""",

    # http://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers = [
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    install_requires = [
'nose',
'setuptools',
'requests'
],
    namespace_packages = ['infi'],

    package_dir = {'': 'src'},
    package_data = {'': []},
    include_package_data = True,
    zip_safe = False,

    entry_points = {
        "console_scripts": [],
        "gui_scripts": [],
        "nose.plugins": ['logbook = infi.nose_plugins.logbook:LogbookPlugin',
                         'stderr = infi.nose_plugins.stderr:LoggingToStderrPlugin',
                         'requests.no.warning = infi.nose_plugins.requestswarnings:RequestsSuppressWarningPlugin',
                        ],
        },
)

if SETUP_INFO['url'] is None:
    _ = SETUP_INFO.pop('url')

def setup():
    from setuptools import setup as _setup
    from setuptools import find_packages
    SETUP_INFO['packages'] = find_packages('src')
    _setup(**SETUP_INFO)

if __name__ == '__main__':
    setup()

