# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Callbacks classes
"""


class Callback(object):
    """ Base class for callbacks.

    The hook_name is the path to the hook, it could be either a module, like
    "package.module", or a specific class "package.module::Class".
    The hook_name is the name of the function to hook_on, it's relative to
    the hook_module, for example with a hook_module equal to
    "package.module::Class" and a hook_path equal to "method", we will
    hook on the method named "method" of a class named "Class" in the module
    named "package.module"
    """

    def __init__(self, hook_module, hook_name, strategy=None):
        self.hook_module = hook_module
        self.hook_name = hook_name
        self.strategy = strategy

    def exception_infos(self, infos={}):
        """ Returns infos in case of exception
        """
        return {}
