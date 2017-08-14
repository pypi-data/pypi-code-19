
from __future__ import absolute_import, division, print_function
import sys
import os
import argparse
from . import is_a

class Settings(object):

    def __init__(self, *args, **kwargs):
        self.__parser = argparse.ArgumentParser()
        self.__arguments = None
        self.__unknowns = None
        self.__env = None
        self.__variables = None  # TODO:add to argparse
        return super(Settings, self).__init__(*args, **kwargs)

    @property
    def parser(self):
        return self.__parser

    @property
    def arguments(self):
        return self.__arguments

    @property
    def unknowns(self):
        return self.__unknowns

    def final_parse(self):
        self.__arguments = self.__parser.parse_args()

    def partial_parse(self):
        self.__arguments, self.__unknowns = self.__parser.parse_known_args()

    def add_argument(self, arguments, action=None, nargs=None, const=None, default=None, type=None, choices=None, required=None, help=None, metavar=None, dest=None, **kw):

        if action is not None:
            kw['action'] = action
        if nargs is not None:
            kw['nargs'] = nargs
        if const is not None:
            kw['const'] = const
        if default is not None:
            kw['default'] = default
        if type is not None:
            kw['type'] = type
        if choices is not None:
            kw['choices'] = choices
        if required is not None:
            kw['required'] = required
        if help is not None:
            kw['help'] = help
        if metavar is not None:
            kw['metavar'] = metavar
        if dest is not None:
            kw['dest'] = dest
        self.__parser.add_argument(*arguments, **kw)

    def int_argument(self, arguments, choices=None, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, type=int, choices=choices, default=default,
                          required=required, help=help, metavar=metavar, dest=dest)

    def string_argument(self, arguments, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, type=str, default=default,
                          required=required, help=help, metavar=metavar, dest=dest)

    def path_argument(self, arguments, default=None, required=None, help=None, metavar=None, dest=None, exists=True):
        self.add_argument(arguments, type=lambda x: self._path(
            exists, x), default=default, required=required, help=help, metavar=metavar, dest=dest)

    def bool_argument(self, arguments, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, type=self._bool, default=default,
                          required=required, help=help, metavar=metavar, dest=dest)

    def feature_argument(self, feature, default, required=None, help=None, metavar=None):
        if default != True and default != False:
            hosts.output.WriteError(
                "Default value for feature has to be a True or False value", show_stack=False)
        self.add_argument(["--enable-{0}".format(feature)], action='store_true',
                          default=default, required=required, help=help, metavar=metavar, dest=feature)
        self.add_argument(["--disable-{0}".format(feature)], action='store_false',
                          default=default, required=required, help=help, metavar=metavar, dest=feature)

    # add option for mapping x -> y values
    def enum_argument(self, arguments, choices, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, choices=choices, type=int, default=default,
                          required=required, help=help, metavar=metavar, dest=dest)
    # add option for mapping x -> y values

    def list_argument(self, arguments,  nargs="*", choices=None, default=None, required=None, help=None, metavar=None, dest=None):
        self.add_argument(arguments, action=extendAction, nargs=nargs, choices=choices,
                          type=str, default=default, required=required, help=help, metavar=metavar, dest=dest)

    def get_argument(self, name):
        return self.__arguments.get(name)

    def _bool(self, arg):

        opt_true_values = set(['y', 'yes', 'true', 't', '1', 'on', 'all'])
        opt_false_values = set(['n', 'no', 'false', 'f', '0', 'off', 'none'])

        tmp = value.lower()
        if tmp in opt_true_values:
            return True
        elif tmp in opt_false_values:
            return False
        else:
            msg = 'Invalid value Boolean value : "{0}"\n Valid options are {0}'.format(value,
                                                                                       opt_true_values | opt_false_values)
            raise argparse.ArgumentTypeError(msg)

    def _path(self, exists, arg):
        path = os.path.abspath(arg)
        if not os.path.exists(path) and exists:
            msg = '"{0}" is not a valid path'.format(path)
            raise argparse.ArgumentTypeError(msg)
        return path

#----------------------
# useful helpful files

def JobValues(arg):
    try:
        j = int(arg)
    except ValueError:
        raise argparse.ArgumentTypeError("Invalid int value {0}".format(arg))
    if j == 0:
        j = 1
    if j < 0:
        msg = 'Must be a postive value'.format(j)
        raise argparse.ArgumentTypeError(msg)
    return j


class extendAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):

        if is_a.Int(nargs) and nargs <= 1:
            raise ValueError(
                'Invalid value for nargs:\n must be "+" or "*" or a number greater than 1')
        elif is_a.String(nargs) and nargs not in ("+", "*"):
            raise ValueError(
                'Invalid value for nargs:\n must be "+" or "*" or a number greater than 1')
        elif not is_a.String(nargs) and not is_a.Int(nargs):
            raise ValueError(
                'nargs for extend actions must be a string or int type')

        super(extendAction, self).__init__(option_strings=option_strings,
                                           dest=dest,
                                           nargs=nargs,
                                           const=const,
                                           default=default,
                                           type=type,
                                           choices=choices,
                                           required=required,
                                           help=help,
                                           metavar=metavar)

    def __call__(self, parser, namespace, values, option_string=None):
        items = []
        for i in values:
            if i[-1] == ',':
                i = i[:-1]
            i = i.split(",")
            items.extend(i)
        setattr(namespace, self.dest, items)