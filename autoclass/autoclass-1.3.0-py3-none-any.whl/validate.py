from inspect import getfullargspec
from typing import Callable, Dict, Any

from decorator import decorate

from autoclass.utils import _create_function_decorator__robust_to_args


def validate(**validators: Dict[str, Callable[[Any], bool]]):
    """
    Defines a decorator with parameters, that will execute the provided input validators PRIOR to executing the 
    function. Specific entry 'returns' may contain validators executed AFTER executing the function.
    
    ```
    def is_even(x):
        return x % 2 == 0
    
    def gt(a):
        def gt(x):
            return x >= a
        return gt
    
    @validate(a=[is_even, gt(1)], b=is_even)
    def myfunc(a, b):
        print('hello')
    ```
    
    will generate the equivalent of :
    
    ```
    def myfunc(a, b):
        gt1 = gt(1)
        if is_even(a) and gt1(a) and is_even(b):
            print('hello')
        else:
            raise ValidationException(...)
    ```
    
    :param validators: 
    :return: 
    """
    return _create_function_decorator__robust_to_args(validate_decorate, **validators)


def validate_decorate(func: Callable, **validators: Dict[str, Callable[[Any], bool]]) -> Callable:
    """
    Defines a decorator with parameters, that will execute the provided input validators PRIOR to executing the 
    function. Specific entry 'returns' may contain validators executed AFTER executing the function.
    
    :param func: 
    :param include: 
    :param exclude: 
    :return: 
    """
    # (1) retrieve function signature
    # attrs, varargs, varkw, defaults = getargspec(func)
    signature_attrs, signature_varargs, signature_varkw, signature_defaults, signature_kwonlyargs, \
    signature_kwonlydefaults, signature_annotations = getfullargspec(func)
    # TODO better use signature(func) ?

    # check that validators dont contain names that are incorrect
    if validators is not None:
        incorrect = set(validators.keys()) - set(signature_attrs)
        if len(incorrect) > 0:
            raise ValueError('@validate definition exception: validators are defined for \'' + str(incorrect) + '\' '
                             'that is/are not part of signature for ' + str(func))

    # (2) create a wrapper around the function so that all .

    # -- old:
    # @functools.wraps(func) -> to make the wrapper function look like the wrapped function
    # def wrapper(self, *args, **kwargs):

    # -- new:
    # we now use 'decorate' at the end of this code to have a wrapper that has the same signature, see below
    def wrapper(func, *args, **kwargs):

        # handle default values and kw arguments
        for attr, val in zip(reversed(signature_attrs), reversed(signature_defaults or [])):
            if attr in validators.keys():
                # set default or provided value
                if attr in kwargs.keys():
                    # provided: we never seem to enter here, why ? maybe depends on the version of python
                    _validate(func, attr, validators[attr], kwargs[attr])
                else:
                    # default
                    _validate(func, attr, validators[attr], val)

        # handle positional arguments
        for attr, val in zip(signature_attrs, args):
            if attr in validators.keys():
                _validate(func, attr, validators[attr], val)

        # handle varargs : since we dont know their name, they can only be validated as a whole
        if signature_varargs:
            remaining_args = args[len(signature_attrs):]
            if signature_varargs in validators.keys():
                _validate(func, signature_varargs, validators[signature_varargs], remaining_args)

        # handle varkw : since we know their names, they can be validated either as a whole or independently
        if signature_varkw:
            # either the validator is for the whole dictionary
            if signature_varkw in validators.keys():
                _validate(func, signature_varkw, validators[signature_varkw], kwargs)
            else:
                # or the validator may be for individual items.
                for attr, val in kwargs.items():
                    if attr in validators.keys():
                        _validate(func, attr, validators[attr], val)

        # finally execute the method
        return func(*args, **kwargs)

    return decorate(func, wrapper)


def _validate(func, name, validator_func, item):
    try:
        for val in validator_func:
            _validate(func, name, val, item)
        return
    except TypeError:
        pass
    if not validator_func(item):
        raise ValidationError.create(func, name, validator_func, item)


class ValidationError(Exception):
    """
    Exception raised whenever validation fails. It may be directly triggered by Validators, or it is raised if 
    validator returns false
    """

    def __init__(self, contents):
        """
        We actually can't put more than 1 argument in the constructor, it creates a bug in Nose tests
        https://github.com/nose-devs/nose/issues/725
        
        Please use ValidationError.create() instead

        :param contents:
        """
        super(ValidationError, self).__init__(contents)

    @staticmethod
    def create(func, name, validator_func, item, extra_msg: str = ''):
        """
        
        :param func: 
        :param name: 
        :param validator_func: 
        :param item: 
        :param extra_msg
        :return: 
        """
        return ValidationError('Error validating input \'' + str(name) + '=' + str(item) + '\' for function \''
                              + str(func) + '\' with validator ' + str(validator_func) + '.\n' + extra_msg)
