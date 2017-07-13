from distutils.core import setup

from setuptools import find_packages


packages = [
    'pyaliyun',
    'pyaliyun.core',
    'pyaliyun.mns',
    'pyaliyun.oss',
]

setup(
    name='pyaliyun',
    version='1.0.5.4',
    # packages=['pyaliyun'],
    packages=packages,
    url='http://www.wantchalk.com',
    # package_dir={'pyaliyun': 'pyaliyun'},
    license='MIT',
    author='vincent wantchalk',
    author_email='ergal@163.com',
    description='Python language sdk and tools for Aliyun service api',
    # What does your project relate to?
    keywords='aliyun oss mns',
    install_requires=['requests>=2.11.1'],
    classifiers=[
        # How mature is this project? Common values are
        # Development Status:: 1 - Planning
        # Development Status:: 2 - Pre - Alpha
        # Development Status:: 3 - Alpha
        # Development Status:: 4 - Beta
        # Development Status:: 5 - Production / Stable
        # Development Status:: 6 - Mature
        # Development Status:: 7 - Inactive
        'Development Status :: 3 - Alpha',
        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        # OS
        'Operating System :: OS Independent',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

)
