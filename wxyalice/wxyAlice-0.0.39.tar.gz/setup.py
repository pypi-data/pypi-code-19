from distutils.core import setup
setup(
    name='wxyAlice',
    packages=['wxyAlice'],
    version='0.0.39',
    description='classes used in micro service on sanic',
    author='wangxiaoyu',
    author_email='wangxiaoyu.wangxiaoyu@gmail.com',
    license='MIT',
    install_requires=[
        'sanic',
        'sanic-cors',
        'requests',
        'PyJWT',
        'jsonschema'
    ],
    url='https://github.com/netsmallfish1977/wxyAlice',
    download_url='https://github.com/netsmallfish1977/wxyAlice/tarball/0.0.39',
    keywords=['wxy', 'Alice', 'sanic', 'restapi'],
    classifiers=[],
)
