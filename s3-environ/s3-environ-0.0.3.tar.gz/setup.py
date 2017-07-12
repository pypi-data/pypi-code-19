from setuptools import setup


setup(
    author='Jonatas Baldin',
    author_email='jonatas.baldin@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    description='Load environment variables from a AWS S3 file!',
    license='MIT License',
    url='https://github.com/jonatasbaldin/s3-environ',
    include_package_data=True,
    name='s3-environ',
    packages=['s3_environ'],
    version='0.0.3'
)
