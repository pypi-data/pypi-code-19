from setuptools import setup


requires = [
    "requests>=2.14.2",
    "urllib3>=1.22",
    "boto3>=1.4.6",
    "botocore>=1.6.4"
]


setup(
    name='hssadmin',
    version='0.2.1',
    description='Cloudian HyperStore(R) Admin API SDK for Python',
    url='https://github.com/ryosuke-mt/hyperstore',
    author='Ryosuke Matsui',
    author_email='lightning@ga2.so-net.ne.jp',
    maintainer='Ryosuke Matsui',
    maintainer_email='lightning@ga2.so-net.ne.jp',
    license='MIT',
    keywords='sample setuptools development',
    packages=[
        "hssadmin"
    ],
    install_requires=requires,
    classifiers=[
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'License :: OSI Approved :: MIT License'
    ],
)
