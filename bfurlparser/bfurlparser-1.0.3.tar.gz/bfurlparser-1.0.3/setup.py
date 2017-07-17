from distutils.core import setup, Extension

# Read the long decription
readme_text = None
with open("README.rst", "r") as r:
    readme_text = r.read()

# Setup
setup(
    name='bfurlparser',
    version='1.0.3',
    description='A blazing fast Python URL parser',
    long_description=readme_text,
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
