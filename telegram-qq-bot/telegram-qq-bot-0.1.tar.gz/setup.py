from setuptools import setup

version = "0.1"
setup(
    name="telegram-qq-bot",
    version=version,
    description="A telegram bot that forwards subscribed messages to telegram",
    author="Extremezhazha",
    author_email="extremezhazha@gmail.com",
    license="GPLv3",
    keywords="python smartqq telegram",
    install_requires=["python-smartqq-client", "pymongo"],
    packages=["telegramqqbot"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Topic :: Communications :: Chat",
        "Environment :: Console",
        "Operating System :: OS Independent"
    ]
)
