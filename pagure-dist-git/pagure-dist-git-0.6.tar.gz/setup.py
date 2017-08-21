from setuptools import setup

f = open('README.rst')
long_description = f.read().strip()
long_description = long_description.split('split here', 1)[1]
f.close()

install_requires = [
    'pdc_client',
    'dogpile.cache',
    'pagure',
]
tests_require = [
    'nose',
    'mock',
]

setup(
    name='pagure-dist-git',
    version='0.6',
    description="Pagure gitolite plugin for Fedora's dist-git setup.",
    long_description=long_description,
    author='Pierre-Yves Chibon',
    author_email='pingou@fedoraproject.org',
    url='https://pagure.io/pagure-dist-git',
    license='GPLv2+',
    install_requires=install_requires,
    tests_require=tests_require,
    test_suite='nose.collector',
    packages=[],
    py_modules=['dist_git_auth'],
    include_package_data=True,
    zip_safe=False,
    entry_points="""
    [pagure.git_auth.helpers]
    distgit = dist_git_auth:DistGitoliteAuth
    """,
)
