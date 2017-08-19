from distutils.core import setup

setup(
    name='telegram-autoposter',
    packages=['telegram_autoposter'],
    version='0.1',
    description='Library for building bot for automatic posting from some source into telegram channels. '
                'Based on python-telegram-bot',
    author='Bachynin Ivan',
    author_email='bachynin.i@gmail.com',
    license='MIT',
    url='https://github.com/vaniakosmos/telegram-autoposter',
    download_url='https://github.com/vaniakosmos/telegram-autoposter/archive/v0.1.tar.gz',
    keywords=['telegram', 'bot'],
    install_requires=[
        'python-telegram-bot',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3.6'
    ],
    python_requires='>=3.6',
)
