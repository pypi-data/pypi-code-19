# -*- coding: utf-8 -*-
# Copyright (c) 2016 Sqreen. All Rights Reserved.
# Please refer to our terms for more information: https://www.sqreen.io/terms.html
""" Base class for JS Callbacks
"""
import logging

from py_mini_racer import py_mini_racer
from py_mini_racer.py_mini_racer import JSEvalException

from ..rules import RuleCallback
from ..binding_accessor import BindingAccessor
from ..runtime_infos import runtime
from ..exceptions import SqreenException
from ..frameworks.blank import BlankRequest
from ..utils import CustomJSONEncoder


LOGGER = logging.getLogger(__name__)


class JSException(SqreenException):
    """ Base exception raised in JSCB
    """
    def __init__(self, message, callback, arguments):
        super(JSException, self).__init__(message)
        self.callback = callback
        self.arguments = arguments

    def exception_infos(self):
        return {'cb': self.callback, 'args': self.arguments}


class JSCB(RuleCallback):
    """ A callback that run a JS function as pre / post / failing through
    py_mini_racer context.
    """

    def __init__(self, *args, **kwargs):
        super(JSCB, self).__init__(*args, **kwargs)

        self._loaded = False
        self.arguments = {}
        self.js_context = None

    def load(self):
        """ Create the js_context and binding accessors
        """

        # Prepare a js context
        self.js_context = py_mini_racer.MiniRacer()

        if self.callbacks:
            for callback_name, callback_args in self.callbacks.items():

                if not isinstance(callback_args, list):
                    source = callback_args
                    self.arguments[callback_name] = []
                else:
                    source = callback_args[-1]
                    arguments = callback_args[:-1]
                    self.arguments[callback_name] = [BindingAccessor(arg) for arg in arguments]

                js_source = "var {} = {}".format(callback_name, source)
                self.js_context.eval(js_source)

        self._loaded = True

    def __getattribute__(self, name):
        """ Lie about pre / post / failing existence if no callbacks is defined
        for them
        """
        if name in ('pre', 'post', 'failing'):
            if name not in self.callbacks:
                err_msg = "'{}' object has no attribute '{}'"
                raise AttributeError(err_msg.format(self.__class__.__name__, name))

        return RuleCallback.__getattribute__(self, name)

    def pre(self, original, *args, **kwargs):
        """ Call the pre JS function with its arguments
        """
        if self._loaded is False:
            self.load()
        return self.execute('pre', self.arguments['pre'], original, None, args, kwargs)

    def post(self, original, return_value, *args, **kwargs):
        """ Call the post JS function with its arguments
        """
        if self._loaded is False:
            self.load()
        return self.execute('post', self.arguments['post'], original, return_value, args, kwargs)

    def failing(self, original, exception, *args, **kwargs):
        """ Call the failing JS function with its arguments
        """
        if self._loaded is False:
            self.load()
        return self.execute('failing', self.arguments['failing'], original, exception, args, kwargs)

    def execute(self, name, arguments, original, return_value, args, kwargs):
        """ Execute a JS callback passed in definition.
        Handle recording attack, observations and chaining.
        Protected against infinite recursion with a max number of JS calls
        set to 100.
        """
        request = runtime.get_current_request()

        # Fallback on a blank request for binding accessor
        if request is None:
            request = BlankRequest()

        # Safeguard against infinite recursion
        for i in range(100):
            binding_eval_args = {
                "binding": locals(),
                "global_binding": globals(),
                "framework": request,
                "instance": original,
                "arguments": args,
                "kwarguments": kwargs,
                "cbdata": self.data,
                "return_value": return_value
            }
            resolved_args = [arg.resolve(**binding_eval_args) for arg in arguments]

            LOGGER.debug("Resolved args %s for %s", resolved_args, arguments)

            try:
                result = self.js_context.call(name, *resolved_args, encoder=CustomJSONEncoder)
            except JSEvalException as e:
                raise JSException(e.args[0], name, resolved_args)

            LOGGER.debug("JS Result %r for %s", result, self.rule_name)

            if result is None:
                return result

            # Process the return value
            self._record_attack(result)
            self._record_observations(result)

            # Check for chaining
            if result.get('call') is None:
                return result

            # Prepare next call
            name = result['call']

            if name not in self.callbacks:
                raise JSException("Invalid callback '{}'".format(name), name, None)

            return_value = result.get('data')

            if result.get('args'):
                arguments = [BindingAccessor(arg) for arg in result['args']]
            else:
                arguments = self.arguments[name]

    def _record_attack(self, return_value):
        """ Record an attack if the JS callback returned a record info
        """
        if return_value.get('record'):
            self.record_attack(return_value['record'])

    def _record_observations(self, return_value):
        """ Record observations if the JS callback returned a observations list
        """
        if return_value.get('observations'):
            for observation in return_value['observations']:
                self.record_observation(*observation)
