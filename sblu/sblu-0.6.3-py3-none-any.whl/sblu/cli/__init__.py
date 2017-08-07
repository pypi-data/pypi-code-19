import os
import sys
import click
import hmac as _hmac
import hashlib as _hashlib

CONTEXT_SETTINGS = dict(auto_envvar_prefix='COMPLEX')


def make_cli_class(package):
    cmd_folder = os.path.abspath(os.path.join(os.path.dirname(__file__),
                                              package))

    class ComplexCLI(click.MultiCommand):

        def list_commands(self, ctx):
            rv = []
            for filename in os.listdir(cmd_folder):
                if filename.endswith('.py') and \
                   filename.startswith('cmd_'):
                    rv.append(filename[4:-3])
            rv.sort()
            return rv

        def get_command(self, ctx, name):
            try:
                if sys.version_info[0] == 2:
                    name = name.encode('ascii', 'replace')
                mod = __import__('sblu.cli.{0}.cmd_{1}'.format(package, name),
                                 None, None, ['cli'])
            except ImportError:
                return
            return mod.cli

    return ComplexCLI

def make_sig(form, secret):
    sig = ""
    for k in sorted(form.keys()):
        if form[k] is not None:
            sig += "{}{}".format(k, form[k])
    return _hmac.new(
        secret.encode('utf-8'), sig.encode('utf-8'), _hashlib.md5).hexdigest()
