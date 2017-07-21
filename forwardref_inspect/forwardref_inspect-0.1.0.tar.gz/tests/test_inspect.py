import forwardref_inspect

from tests.foo import Foo


def test_forward_reference_str_parameters_annotation():
    signature = forwardref_inspect.signature(Foo.__eq__)
    assert signature.parameters['other'].annotation == Foo


def test_forward_reference_mixed_parameters_annotation():
    signature = forwardref_inspect.signature(Foo.method_with_mixed_annotations)
    assert signature.parameters['other'].annotation == Foo
    assert signature.parameters['flag'].annotation == bool


def test_forward_reference_str_return_annotation():
    signature = forwardref_inspect.signature(Foo.build)
    assert signature.return_annotation == Foo
