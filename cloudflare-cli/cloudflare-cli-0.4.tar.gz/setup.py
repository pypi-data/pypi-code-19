import os
from setuptools import find_packages, setup

requirements = [
    'cloudflare',
    'dnspython'
]

if os.name == 'posix':
    requirements.append('sh')


setup(name = "cloudflare-cli",
    install_requires = requirements,
    version = "0.4",
    description = "A command line tool for managing vCenter and ESXi servers",
    author = "Moshe Immerman",
    author_email = 'name.surname@gmail.com',
    platforms = ["any"],
    license = "BSD",
    url = "http://github.com/Moshe-Immerman/cloudflare-cli",
    packages = find_packages(),
    entry_points = {
        "console_scripts": [
            "cloudflare = cloudflare_cli.Cloudflare:main",
        ]
    }
)