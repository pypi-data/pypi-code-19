from setuptools import setup

setup(
    name='lwe-mjs',
    version='0.4.0',
    description='A JSON-Server component which uses the mapper project',
    long_description='For an overview and some examples, head over to '
                     '`Github <https://github.com/linuxwhatelse/mjs>`_',
    url='https://github.com/linuxwhatelse/mjs',
    author='linuxwhatelse',
    author_email='info@linuxwhatelse.com',
    license='GPLv3',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    keywords='mapper json server mjs',
    py_modules=[
        'mjs'
    ],
    install_requires=[
        'lwe-mapper >= 1.2.1'
    ],
)
