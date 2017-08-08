from setuptools import setup, find_packages
import oss2_storage


def read(filename):
    with open(filename) as f:
        return f.read()


def get_requirements_tests():
    with open('requirements-tests.txt') as f:
        return f.readlines()


setup(
    name='django-oss2-storage',
    version=oss2_storage.__version__,
    packages=find_packages(),
    author='Kevis Wang',
    author_email='keviswang@outlook.com',
    license='BSD',
    description='Support for aliyun oss2 storage backends in Django',
    long_description=read('README.rst') + '\n\n' + read('CHANGELOG.rst'),
    url='https://github.com/keviswang/django-oss2-storage',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    install_requires=['oss2', 'django>=1.10'],
    zip_safe=False
)
