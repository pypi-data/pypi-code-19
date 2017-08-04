# coding: utf-8
"""
Contains the class FactoryBuild.
"""

class Dependency(object):
    """
    This class represents a dependency used by the factory to build an object
    """
    def __init__(self, class_path, method=None, args=None, kwargs=None):
        self.class_path = class_path
        self.method = method
        self.kwargs = kwargs or {}
        self.args = args or ()

    def inject(self, factory):
        """
        Inject the class build from the dependency using the factory given in parameter.
        Args:
            factory (Factory): The factory used to build the class.
        """
        instance = factory.build(class_path=self.class_path)

        if self.method:
            method = getattr(instance, self.method)
            return method(*self.args, **self.kwargs)
        else:
            return instance
