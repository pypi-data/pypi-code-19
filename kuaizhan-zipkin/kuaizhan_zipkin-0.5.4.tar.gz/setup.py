from setuptools import setup, find_packages

setup(
    name='kuaizhan_zipkin',
    version='0.5.4',
    keywords='kuaizhan zipkin',
    description='kuaizhan zipkin sender',
    license='MIT License',
    url='',
    author='xuchen',
    author_email='chenxu211618@sohu-inc.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=['thriftpy', 'py_zipkin', 'kafka', 'bottle'],
)
