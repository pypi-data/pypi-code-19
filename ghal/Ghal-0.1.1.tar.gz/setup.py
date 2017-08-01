from distutils.core import setup

setup(
        name='Ghal',
        author='Robert D. French',
        author_email='robert@robertdfrench.me',
        version='0.1.1',
        description='Githost Abstraction Layer. One library to rule them all',
        url='https://github.com/robertdfrench/ghal',
        packages=['ghal'],
        install_requires=['PyGithub','python-gitlab'],
        python_requires='>=3.6'
        )
