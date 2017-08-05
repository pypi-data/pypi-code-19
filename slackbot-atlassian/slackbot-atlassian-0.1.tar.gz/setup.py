from setuptools import setup, find_packages
from os import path

here = path.abspath(path.dirname(__file__))

description = 'Slackbot plugins for the Atlassian suite'
with open('requirements.txt') as f:
    required = f.read().splitlines()

setup(
    name='slackbot-atlassian',
    version='0.1',
    description=description,
    long_description=description,
    url='https://github.com/DandyDev/slackbot-atlassian',
    author='Daan Debie',
    author_email='debie.daan@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
    ],
    keywords='slack atlassian jira bamboo',
    packages=find_packages(),
    python_requires='>=3',
    install_requires=required
)
