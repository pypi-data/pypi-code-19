from glob import glob
import os
import subprocess
import sys

import terrapy.const as const
from .emit import TfJsonEmitter


def terraform_wrap(args):
    TfJsonEmitter.walk_current_dir()
    cmd = ['terraform'] + args
    subprocess.run(cmd)


def get_intercept(args):
    """
    if args are something that should be handled by terrapy, not
    terraform, indicate and yield cmd name
    """
    is_intercept = False
    mod_args = None
    if len(args) > 0 and args[0] == 'clean':
        is_intercept = True
        mod_args = ['clean']

    return is_intercept, mod_args


def run_intercept_cmd(mod_args):
    cmd_name = mod_args[0]
    # cmd_args = mod_args[1:]
    if cmd_name == 'clean':
        for filename in glob(const.out_glob, recursive=True):
            os.remove(filename)
    else:
        raise ValueError('bad cmd {}'.format(cmd_name))


def main():
    sys.path.append(os.getcwd())
    args = sys.argv[1:]
    is_intercept, mod_args = get_intercept(args)
    if is_intercept:
        run_intercept_cmd(mod_args)
    else:
        terraform_wrap(args)
