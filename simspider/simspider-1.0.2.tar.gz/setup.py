from setuptools import setup, find_packages

setup(
    name="simspider",
    version="1.0.2",
    keywords=["crawl", "spider", "定向爬虫"],
    description="简单的定向爬虫框架",
    license="MIT",
    author="陈粮",
    author_email="1570184051@qq.com",
    packages=find_packages(),
    platforms="any",
    install_requires=["chardet>=3.0.2"],
    entry_points={
        'console_scripts': [
            'simcode=simspider.simcode:main',
            'simgo=simspider.simgo:main',
            'simtest=simspider.simtest:main'
        ],
    },
    zip_safe=False
)
