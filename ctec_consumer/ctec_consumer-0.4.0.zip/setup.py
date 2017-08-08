import setuptools

version = '0.4.0'

setuptools.setup(
        name='ctec_consumer',
        version=version,
        packages=setuptools.find_packages(),
        author='ZhangZhaoyuan',
        author_email='zhangzhy@chinatelecom.cn',
        url='http://www.189.cn',
        description='189 rabbitMQ consumer',
        install_requires=['kombu==3.0.35', 'gevent==1.2.1', 'pika==0.10.0']
)
