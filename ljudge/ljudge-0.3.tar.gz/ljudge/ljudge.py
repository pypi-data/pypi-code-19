# encoding: utf-8

from __future__ import print_function

import subprocess
import collections
import json

basestring_type = basestring if type('') is type(b'') else str


def options_to_args(opts):
    if isinstance(opts, collections.Mapping):
        for key, val in opts.items():
            assert isinstance(key, basestring_type)
            yield '--' + key
            for v in options_to_args(val):
                yield v
    elif isinstance(opts, collections.Iterable) and not isinstance(opts, basestring_type):
        for opt in opts:
            for v in options_to_args(opt):
                yield v
    else:
        yield str(opts)


def run(options={}, env={}):
    args = ['ljudge']
    args.extend(options_to_args(options))
    args.extend(options_to_args(env))
    sp = subprocess.Popen(args, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    out, err = sp.communicate()
    if sp.returncode != 0:
        cmd = subprocess.list2cmdline(args)
        print(err)
        raise subprocess.CalledProcessError(sp.returncode, cmd, err)
    return json.loads(out)
