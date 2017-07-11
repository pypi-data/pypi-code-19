from setuptools import setup


setup(
    name='pytgram',
    version='0.0.2',
    packages=['pytgram', 'tests'],
    url='https://github.com/artcom-net/pytgram',
    license='MIT',
    author='Artem Kustov',
    author_email='artem.kustov@artcom-net.ru',
    description='Library to create Telegram Bot based on Twisted',
    long_description=open('README.rst').read(),
    install_requires=open('requirements.txt').read().split(),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Twisted',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
        'Operating System :: POSIX :: BSD :: FreeBSD',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Software Development :: Libraries',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: HTTP Servers',

    ]
)
