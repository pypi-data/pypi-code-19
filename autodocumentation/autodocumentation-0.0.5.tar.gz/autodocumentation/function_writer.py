try:
    from inspect import signature
except:
    from funcsigs import signature

from autodocumentation.doc_builder import DocBuilder
from autodocumentation.flask_writer import FlaskRequestWriter, BaseWriter
from autodocumentation.compat import decode_repr

class FunctionWriter(BaseWriter):
    def serialize(self, func, output, *a, **k):
        sig = signature(func)
        params = sig.bind(*a, **k)
        return dict(
            name=func.__name__,
            output=decode_repr(repr(output)),
            arguments=[
                [key, decode_repr(repr(value))]
                for key, value in params.arguments.items()
            ]
        )