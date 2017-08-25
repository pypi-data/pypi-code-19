#!/usr/bin/env python
# -*- coding: utf8 -*-

try:
    from superkwargs import exceptions
    from superkwargs import inject_kwargs, restore_function
except ImportError:
    import exceptions
    from inject import inject_kwargs, restore_function

def kwarg(name, required=False, default=None, evaluate_default=False,
          choices=None, validation_test=None, type_=None):
    def decorator(function):
        def superkwarg(*args, **kwargs):
            if len(args) > 0:
                raise exceptions.PositionalArgsIncludedException(
                    'Positional argument \'{arg}\' not allowed; kwargs are required'.format(
                        arg=args[0]
                    ))

            if required and name not in kwargs:
                raise exceptions.MissingRequiredKwargException(
                    'Keyword argument \'{arg}\' required to invoke \'{func}\''.format(
                        arg=name, func=function.__name__))

            if name not in kwargs:
                kwargs[name] = default(kwargs) if evaluate_default else default

            if type_ is not None and not isinstance(kwargs[name], type_):
                raise exceptions.WrongKwargValueTypeException(
                    'Keyword argument \'{arg}\' value \'{value}\' type \'{value_type}\' does not match expected type \'{expected_type}\''.format(
                        arg=name,
                        value=kwargs[name],
                        value_type=type(kwargs[name]),
                        expected_type=type_
                    )
                )

            if choices is not None and kwargs[name] not in choices:
                raise exceptions.InvalidKwargValueException(
                    'Keyword argument \'{arg}\' value \'{value}\' not in available choices {choices}'.format(
                        arg=name,
                        value=kwargs[name],
                        choices=choices
                    )
                )

            if validation_test is not None and not validation_test(kwargs[name]):
                raise exceptions.KwargValueValidationException(
                    'Keyword argument \'{arg}\' value \'{value}\' failed validation test'.format(
                        arg=name,
                        value=kwargs[name]
                    )
                )

            return function(**kwargs)
        return superkwarg
    return decorator


def superkwarg(inject=False):    
    def decorator(function):
        def configure(**kwargs):        
            if inject:
                try:
                    _blank, state = inject_kwargs(kwargs, function)
                    return function()
                finally:
                    restore_function(function, _blank, state)

            return function(**kwargs)
        return configure
    return decorator
