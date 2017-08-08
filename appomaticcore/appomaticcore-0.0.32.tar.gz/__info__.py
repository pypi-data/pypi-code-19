version = "0.0.32"
author = "RedHog (Egil Moeller)"
author_email = "egil.moller@freecode.no"
license = "GPL"
url = "http://github.com/redhog/appomatic"
name = "appomaticcore"
description = "Appomatic is a userfriendly Django environment with automatic plugin (app) management based on pip."
keywords = "appomatic django apps pip"
install_requires = ['django>=1.6', 'pip>=1.5.6']
scripts = ['wsgi.py']
entry_points = {'console_scripts': [
        'appomatic = appomatic.manage:main',
        ]}
