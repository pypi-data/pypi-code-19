from setuptools import setup

setup(
    name='django-setting',
    version='0.1.4',
    description='Help set up project for Deployment, Docker, Secret key management',
    author='lhy',
    author_email='dev@azelf.com',
    license='MIT',
    packages=['django_setting'],
    package_data={
        'django_setting': [
            'files/*',
        ]
    },
    zip_safe=False,
    scripts=['bin/django-setting'],
)
