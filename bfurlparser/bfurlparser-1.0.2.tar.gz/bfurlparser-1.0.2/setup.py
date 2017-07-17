from distutils.core import setup, Extension

setup(
    name='bfurlparser',
    version='1.0.2',
    description='A blazing fast Python URL parser',
    long_description='bfurlparse is a really fast URL parser written in C and ready to be used in Python',
    url='https://github.com/davidfoliveira/py-bfurlparser',
    author='David Oliveira',
    author_email='d.oliveira@prozone.org',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Internet :: WWW/HTTP',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7'
    ],
    keywords='url parser fast',
    ext_modules=[Extension("bfurlparser", ["bfurlparser.c"])]
)
