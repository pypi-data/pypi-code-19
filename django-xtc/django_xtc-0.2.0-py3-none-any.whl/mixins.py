import copy
import os

from django.template import Context

__all__ = (
    'TemplateContextMixin',
    'FilesystemAssertionsMixin',
)


class TemplateContextMixin(object):
    template_context = {'TESTING__': True}
    """ Dictionary holding the template variable names (keys) and their
    values. """

    def __init__(self, *args, **kwargs):
        self._initial_template_context = copy.deepcopy(self.template_context)
        super().__init__(*args, **kwargs)

    @property
    def initial_template_context(self) -> dict:
        return self._initial_template_context

    def set_context_defaults(self, **defaults) -> None:
        """
        Set defaults for the template context

        Convenience wrapper for `dict.setdefault()`, setting default values
        for all keyword arguments provided.

        :param defaults: Default keys and their values
        :type defaults: dict
        """
        for k, v in defaults.items():
            self.template_context.setdefault(k, v)

    def get_context(self, **additional) -> Context:
        """
        Get a template context and update it with additional key/value pairs.

        Returns the template context, optionally updated with the provided
        key/value pairs. This returns a fresh context each time and as such
        can be reused.

        :param additional: Key/value pairs to be added to the context
        :type additional: dict
        :return: The template context
        """
        if additional:
            self.template_context.update(additional)

        return Context(dict_=self.template_context)

    def reset_template_context(self) -> None:
        """
        Resets the current template context to it's initial value.

        The initial value is set by :meth:`__init__` and is a deepcopy of the
        context defined at the class level.
        For convenience, the variable 'TESTING__' is defined by default,
        so that templates can insert fixed values if this variable is defined or
        disable access to middleware components like the request or view object.

        Access to :attr:`initial_template_context` is made read-only in version
        0.2.0 to prevent footshooting.
        """
        self.template_context = self.initial_template_context


# noinspection PyPep8Naming,PyUnresolvedReferences
class FilesystemAssertionsMixin(object):
    __doc__ = """
    Easy access to filesystem assertions

    Provides access to assertions that test if the filesystem is in a certain
    state.
    """

    def assertFileExists(self, path) -> None:
        """
        Assert that a given file exists and is a file

        :param path: resolvable path to a file
        :type path: str
        :raises AssertionError: if the path does not exist or is not a file
        """
        self.assertTrue(
            os.path.exists(path), "File {} does not exist".format(path)
        )
        self.assertTrue(
            os.path.isfile(path), "Path {} is not a file".format(path)
        )

    def assertDirExists(self, path) -> None:
        """
        Assert that a given directory exists and is a directory

        :param path: a resolvable path
        :type path: str
        :raises AssertionError: if the path does not exist or is not a directory
        """
        self.assertTrue(
            os.path.exists(path), "Directory {} does not exist".format(path)
        )
        self.assertTrue(
            os.path.isdir(path), "Path {} is not a directory".format(path)
        )

    def assertPathNotExists(self, path) -> None:
        """
        Assert that a given path does not exist

        Note: this does not take into account the type of the node if the
        path does exist. It simply verifies if the node is there.

        :param path: resolvable path
        :type path: str
        :raises AssertionError: If the path exists
        """
        self.assertFalse(
            os.path.exists(path), "Path {} exists".format(path)
        )

    def assertDirEmpty(self, path) -> None:
        """
        Assert that a given directory is empty

        :param path: resolvable path to a directory
        :type path: str
        :raises AssertionError: If the path is not a directory or does not exist
        :raises AssertionError: If the path is a directory, but is not empty.
        """
        self.assertDirExists(path)
        self.assertFalse(
            bool(os.listdir(path)), "Directory {} not empty".format(path)
        )

    def assertDirNotEmpty(self, path) -> None:
        """
        Assert that a given directory is not empty

        :param path: resolvable path to a directory
        :type path: str
        :raises AssertionError: If the path is not a directory or does not exist
        :raises AssertionError: If the path is a directory, but is empty.
        """
        self.assertTrue(
            bool(os.listdir(path)), "Directory {} is empty".format(path)
        )


