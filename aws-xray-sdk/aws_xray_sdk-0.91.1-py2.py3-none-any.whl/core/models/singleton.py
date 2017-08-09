class Singleton:
    """
    A decorator class to be used on singleton classes. The decorated class
    can define one `__init__` function that takes only the `self` argument.
    Also, the decorated class cannot be inherited from.

    To access the singleton instance, use the `instance` method. Otherwise
    a `TypeError` will be raised.
    """
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        """
        Returns the singleton instance. Upon its first call, it creates a
        new instance of the decorated class and calls its `__init__` method.
        On all subsequent calls, the already created instance is returned.
        """
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)
