from setuptools import setup, find_packages

setup(
    name="mmogocms",
    version="0.0.9",
    description="Django custom apps to help you get up and running quickly.",
    long_description="Django custom apps to help you get up and running quickly.",
    author="Mmogo Digital",
    author_email="dev@mmogodigital.com",
    license="BSD",
    test_suite="setuptest.setuptest.SetupTestSuite",
    url="http://github.com/mmogodigital/mmogocms",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "django",
        "django-mptt",
        "django-countries",
        "django-taggit",
        "Pillow",
    ],
    tests_require=[
        "tox"
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
)
