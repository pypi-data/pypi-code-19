from setuptools import setup

def readme():
    with open('README.md') as f:
        return f.read()


setup(
    name='py-instrumenting-zipkin',
    version='1.0.0',
    description=(
        'Zipkin based python instrumenting library'
        ' to sends data using sync/async trasnporters.'
    ),
    long_description=readme(),
    keywords='Django Zipkin Instrumentation',
    url='https://github.com/harkishan81001/py-instrumenting',
    author='Hari Kishan',
    author_email='hari.kishan81001@gmail.com',
    license='Apache License 2.0',
    packages=['pytracing'],
    include_package_data=True,
    install_requires= [
        'py-zipkin==0.8.0',
        "Django >= 1.8.1",
    ],
)
