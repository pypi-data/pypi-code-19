# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

class InvalidTransformException(Exception):
    """Raised when the transform is invalid."""

    def __init__(self, message):
        """Initializes a new instance."""
        self.message = message

class Transform:
    """The function that transforms the transcacts."""

    def __init__(self, model, transform_function):
        """Initializes a new instance."""
        self._model = model
        self._transform_function = transform_function

    def get_model(self):
        """Return the corresponding simulation model."""
        return self._model

    def read(self, transact_comp):
        """Return the corresponding computation."""
        return self._transform_function(transact_comp)

def expect_transform(transform):
    """Expect the argument to be a transform."""
    if isinstance(transform, Transform):
        pass
    else:
        raise InvalidTransformException('Expected a transform: ' + str(transform))

def identity_transform(model):
    """Get a transform that returns the identical transact."""
    func = lambda code: '(return ' + code + ')'
    return Transform(model, func)

def compose_transforms(transform_1, transform_2):
    """Compose two specified transforms: transform_1 and then transform_2 to its result."""
    f1 = transform_1
    f2 = transform_2
    if f1.get_model() != f2.get_model():
        raise InvalidTransformException('Expected two transforms to belong to the same model: ' + str(f1) + ', ' + str(f2))
    func = lambda code: '(do { z <- ' + f1.read(code) + '; ' + f2.read('z') + '})'
    return Transform(f1.get_model(), func)
