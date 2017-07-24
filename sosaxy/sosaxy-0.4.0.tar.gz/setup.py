from setuptools import setup

def version():
    with open('VERSION', 'r') as f:
        return f.read()

setup(
    name='sosaxy',
    version=version().strip(),
    description='xml processing utility',
    url='http://github.com/xianwill/py-sosaxy',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Topic :: Text Processing :: Markup :: XML',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6'
    ],
    author='Christian Williams',
    author_email='xianwill79@gmail.com',
    license='MIT',
    keywords='xml sax json',
    packages=['sosaxy'],
    include_package_data=True,
    install_requires=[
        
    ],
    entry_points={
        'console_scripts': ['sosaxy=sosaxy.command_line:main']
    },
    test_suite='nose.collector',
    tests_require=['nose'],
    zip_safe=False
)
