"""
Usage: get-addons [-m] path1 [path2 ...]
Given a list  of paths, finds and returns a list of valid addons paths.
With -m flag, will return a list of modules names instead.
"""

import ast
import os
import sys
import fileinput

MANIFEST_FILES = ['__odoo__.py', '__openerp__.py', '__terp__.py', '__manifest__.py']


def is_module(path):
    """return False if the path doesn't contain an odoo module, and the full
    path to the module manifest otherwise"""

    if not os.path.isdir(path):
        return False
    files = os.listdir(path)
    filtered = [x for x in files if x in (MANIFEST_FILES + ['__init__.py'])]
    if len(filtered) == 2 and '__init__.py' in filtered:
        return os.path.join(
            path, next(x for x in filtered if x != '__init__.py'))
    else:
        return False


def is_installable_module(path):
    """return False if the path doesn't contain an installable odoo module,
    and the full path to the module manifest otherwise"""
    manifest_path = is_module(path)
    if manifest_path:
        manifest = ast.literal_eval(open(manifest_path).read())
        if manifest.get('installable', True):
            return manifest_path
    return False


def get_modules(path):

    # Avoid empty basename when path ends with slash
    if not os.path.basename(path):
        path = os.path.dirname(path)

    res = []
    if os.path.isdir(path):
        res = [x for x in os.listdir(path)
               if is_installable_module(os.path.join(path, x))]
    return res


def is_addons(path):
    res = get_modules(path) != []
    return res


def get_addons(path):
    res = []
    addons_found = []
    if not os.path.exists(path):
        return res
    if is_addons(path):
        res.append(path)
        addons_found.append(path)
    for base, dirs, files in os.walk(path):
        for directory in dirs:
            dir_path = os.path.join(base, directory)
            if base in addons_found:
                addons_found.append(dir_path)
                continue
            if is_addons(dir_path):
                res.append(dir_path)
                addons_found.append(dir_path)
    return res


def main(argv=None):
    if argv is None:
        argv = sys.argv
    params = argv[1:]
    if not params:
        print(__doc__)
        return 1

    list_modules = False
    exclude_modules = []
    odoo_path = '/home/odoo/instance/odoo/addons'
    enterprise_path = False

    while params and params[0].startswith('-'):
        param = params.pop(0)
        if param == '-m':
            list_modules = True
        if param == '-e':
            exclude_modules = [x for x in params.pop(0).split(',')]

    func = get_modules if list_modules else get_addons
    paths = params[0].split(',')
    addons_paths = []
    for path in paths:
        addons_paths.append(func(path))
    res = [x for l in addons_paths for x in l]
    if exclude_modules:
        res = [x for x in res if x not in exclude_modules]
    for path in res:
        if os.path.basename(path) == 'enterprise':
            enterprise_path = path
            res.remove(path)
    addons = ','.join(res)
    if enterprise_path:
        addons_path = '{enterprise},{odoo},{addons}'.format(enterprise=enterprise_path,
                                                            odoo=odoo_path,
                                                            addons=addons)
    else:
        addons_path = '{odoo},{addons}'.format(odoo=odoo_path, addons=addons)
    for line in fileinput.input('/home/odoo/.openerp_serverrc', inplace=True):
        if 'addons_path' in line:
            parts = line.split('=')
            new_str = '{field} = {addons}'.format(field=parts[0], addons=addons_path)
            print new_str.replace('\n', '')
        else:
            print line.replace('\n', '')

if __name__ == "__main__":
    sys.exit(main())
