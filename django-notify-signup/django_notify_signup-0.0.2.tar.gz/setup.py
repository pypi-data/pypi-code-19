from setuptools import setup

DESCRIPTION = "Receive a notification for all user registrations."


setup(
    name="django_notify_signup",
    version="0.0.2",
    url='https://github.com/nickromano/django-notify-signup',
    license='MIT',
    description=DESCRIPTION,
    long_description=DESCRIPTION,
    author='Nick Romano',
    author_email='nick.r.romano@gmail.com',
    packages=['django_notify_signup'],
    install_requires=[
        'Django>=1.8',
        'celery',
    ],
    classifiers=[
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    tests_require=[
        'mock'
    ],
    test_suite='testrunner.runtests'
)
