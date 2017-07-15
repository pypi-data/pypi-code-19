# -*- coding: utf-8 -*-
# License GPL-3.0 or later (http://www.gnu.org/licenses/gpl).

import os
import json

MANIFEST_FILE = 'manifest.json'

MANIFEST = {
    "name": "My Apps Title",
    "description": """Multi lines description""",
    "website": "http://",
    "repository": "http://",
    "logo": "logo.png",
    "success_url": "/success",
    "media_url": {},
    "env": {},
    "templates": {},
}


def create_manifest(path=''):
    """
    Manifest is a JSON file, localte at .platform by default
    We can found it also at the root path
    """
    if not path:
        return False

    mf = os.path.join(path, MANIFEST_FILE)

    if not os.path.lexists(mf):
        with open(mf, 'w') as fd:
            fd.write(json.dumps(MANIFEST, indent=2))

    return True


def create_folder(path='', gitkeep=False):
    """
    Create a folder in the location given, if gitkeep parameter
    is true, we add an empty file in this folder, to be Git compatible
    """
    if not os.path.lexists(path):
        os.mkdir(path)
    if gitkeep:
        git_file = os.path.join(path, '.gitkeep')
        with open(git_file, 'w') as fd:
            fd.write('# This is unused, only for git compatibility')

    return True
