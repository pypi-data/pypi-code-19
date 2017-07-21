from setuptools import setup

setup(
    name='normal_forms',
    version='0.2',
    description='Normal forms of dynamical systems',
    keywords='normal form differential equation dynamical system bifurcation',
    url='https://github.com/joepatmckenna/normal_forms',
    author='Joseph P. McKenna',
    author_email='joepatmckenna@gmail.com',
    license='MIT',
    packages=['normal_forms'],
    install_requires=['numpy', 'sympy','copy'],
    zip_safe=False)
