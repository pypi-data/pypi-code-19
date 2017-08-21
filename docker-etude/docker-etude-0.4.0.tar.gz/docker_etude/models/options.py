"""
A set of user-defined options.

Allows modules to enable contingent behavior on composition models, e.g. based on CLI input.

"""


class Options:

    def __getattr__(self, key):
        """
        Return None for missing attribute.

        """
        return None
