import sys
from inspect import Signature
from typing import Callable


def convert_str_annotation(obj, str_annotation):
    """
    Retrieve a callable named `str_annotation`
    in the module of `obj`
    """
    return getattr(sys.modules[obj.__module__], str_annotation)


class ForwardRefSignature(Signature):
    @classmethod
    def from_callable(cls, obj, *, follow_wrapped=True):
        signature = super(ForwardRefSignature, cls).from_callable(obj, follow_wrapped=follow_wrapped)
        signature.convert_parameters(obj)
        signature.convert_return_annotation(obj)
        return signature

    def convert_parameters(self, obj):
        parameters = super(ForwardRefSignature, self).parameters.copy()
        for key in parameters:
            if type(parameters[key].annotation) is str:
                type_annotation = convert_str_annotation(obj, parameters[key].annotation)
                parameters[key] = parameters[key].replace(annotation=type_annotation)
        self._parameters = parameters

    def convert_return_annotation(self, obj):
        return_annotation = super(ForwardRefSignature, self).return_annotation
        if type(return_annotation) is str:
            self._return_annotation = convert_str_annotation(obj, return_annotation)


def signature(callable: Callable) -> ForwardRefSignature:
    return ForwardRefSignature.from_callable(callable)
