from setuptools import setup, find_packages

import collabi

setup(
    name='collabi',
    version=collabi.__version__,
    description=collabi.__doc__.strip(),
    long_description='more stuff',
    url='https://github.com/UnityTech/unitycloud-collab-cli',
    author=collabi.__author__,
    author_email='collabsupport@unity3d.com',
    license=collabi.__license__,
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'collabi = collabi.__main__:main',
        ],
    },
    install_requires=[
        'python-dateutil>=1.5, <2.0',
        'requests>=2.10.0, <2.11.0',
        'grequests>=0.3.0, <0.4.0',
        'humanize>=0.5.0, <0.6.0',
        'tabulate>=0.7.0, <0.8.0',
        'send2trash>=1.3.0, <1.4.0',
        'tqdm>=4.8.0, <4.9.0',
        'keyring>=9.3.0, <9.4.0',
        'filelock>=2.0.0, <2.1.0',
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development',
        'Topic :: Terminals',
        'Topic :: Utilities'
    ],
)
