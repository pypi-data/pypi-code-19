from setuptools import setup

setup(
    name='hypers oauth2',
    version='0.1',
    description='Hypers HFA OAuth 2 API Python SDK',
    url='https://git.hypers.com/hfa/oauth2_sdk',
    author='Changjian Zhu',
    author_email='daya0576@gmail.com',
    license='MIT',
    packages=['hfa_oauth_sdk'],
    install_requires=['requests', 'six'],
    zip_safe=False
)
