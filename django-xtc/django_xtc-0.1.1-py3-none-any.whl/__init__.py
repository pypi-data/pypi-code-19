import copy
import os
import shutil

from django.conf import settings
from django.template import (Template, TemplateDoesNotExist, Context,
                             TemplateSyntaxError)
from django.test import SimpleTestCase
from django.test import TestCase as DjangoTestCase

# noinspection PyProtectedMember
from unittest.case import _AssertRaisesContext as AssertRaisesContext, TestCase

__all__ = (
    'TemplateContextMixin',
    'FilesystemAssertionsMixin',
    'TemplateTestBase',
    'TemplateTestCase',
    'TemplateWithDbTestCase',
)


class TemplateContextMixin(object):
    template_context = {'TESTING__': True}

    def __init__(self, *args, **kwargs):
        self.initial_template_context = copy.deepcopy(self.template_context)
        super().__init__(*args, **kwargs)

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

    def reset_template_context(self):
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
        self.assertFalse(
            bool(os.listdir(path)), "Directory {} not empty".format(path)
        )

    def assertDirNotEmpty(self, path) -> None:
        self.assertTrue(
            bool(os.listdir(path)), "Directory {} is empty".format(path)
        )


# noinspection PyPep8Naming
class TemplateTestBase(TemplateContextMixin, FilesystemAssertionsMixin,
                       TestCase):
    __doc__ = """
    Base class for template test case
    """
    template_test_dir = None
    """ Root directory for templates """
    maxDiff = None
    """ Attempt to not trim output, as in most cases it's not useful. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if not cls.template_test_dir:
            cls.template_test_dir = os.path.abspath(settings.TEMPLATE_TEST_DIR)
        else:
            cls.template_test_dir = os.path.abspath(cls.template_test_dir)
        cls._expect_dir = os.path.join(cls.template_test_dir, 'expect')
        cls._actual_dir = os.path.join(cls.template_test_dir, 'actual')
        cls._source_dir = os.path.join(cls.template_test_dir, 'src')

    def setUp(self):
        self.assertDirExists(self.template_test_dir)
        self.cleanActualDir()
        super().setUp()

    def render_template(self, filename, extra=None, save=False) -> tuple:
        """
        Render a template optionally saving it's output

        Renders a given template file, using the provided context and
        optionally saves the output to the ``actual`` subdirectory of the
        configured `template_test_dir`.

        :param filename: template to test, relative to :attr:`template_test_dir`
        :type filename: str
        :param extra: Extra key/value pairs for the template context
        :type extra: dict
        :param save: Whether to save the output
        :type save: bool
        :return: A 2-tuple consisting of the template output and path to the
                 filename if save was set to true. If save was set to `False`,
                 the second member will be `None`.

        """
        extra = extra or dict()
        ctx = self.get_context(**extra)
        path = filename
        if not filename.startswith('/'):
            path = os.path.join(self._source_dir, filename)

        if not os.path.exists(path):
            raise TemplateDoesNotExist(
                'No such source template',tried=[filename]
            )

        with open(path, 'rt') as f:
            _input = f.read()
            f.close()

        tpl = Template(_input)
        output = tpl.render(ctx)
        actual = None
        if save:
            actual = os.path.join(self._actual_dir, filename)
            with open(actual, 'wt') as f:
                f.write(output)
                f.close()
            self.assertFileExists(actual)
        return output, actual

    def cleanActualDir(self) -> None:
        """
        Clean the "actual" subdirectory

        Cleans the "actual" subdirectory of the :attr:`template_test_dir`,
        so that file exists assertions are valid. It is called on the start
        of a test case, but should be called explicitedly if templates are
        reused within tests of a test case.

        It is not called at :meth:`~unittest.TestCase.tearDown` time, to allow
        post-mortem analysis, which is the primary goal of the saving the
        template output to begin with.

        :raises OSError: For any of the reasons :func:`os.mkdir` can fail
        :raises AssertionError: If after removal and recreation the directory is
                not empty.
        """
        shutil.rmtree(self._actual_dir, ignore_errors=True)
        os.mkdir(self._actual_dir)
        self.assertDirEmpty(self._actual_dir)

    def assertTemplateEqual(self, name: str, context: dict = None,
                            save=False) -> None:
        """
        Test if the rendered output of a template is equal to the expected

        Renders the given template and compares the output to the expected
        output. How these are resolved is documented in
        :class:`TemplateTestCase`.

        :param name: name of the template
        :type name: str
        :param context: template context variables
        :type context: dict
        :param save: whether to save the actual output
        :type save: bool
        :raises AssertionError: If the expected and actual output differ
        """
        context = context or {}
        actual, actual_path = self.render_template(name, context, save=save)

        if not name.startswith('/'):
            expect_path = os.path.join(self._expect_dir, name)
        else:
            expect_path = os.path.join(
                self._expect_dir, os.path.basename(name))

        with open(expect_path, 'rt') as f:
            expected = f.read()
            f.close()

        try:
            self.assertEqual(expected, actual)
        except AssertionError:
            if save:
                raise AssertionError(
                    'Template outputs differ. Run: diff -u {:s} {:s} for '
                    'full diff'.format(expect_path, actual_path)
                )
            raise

    def assertSyntaxError(self, *args, **kwargs):
        """
        Test that a template causes a syntax error

        Assertion method especially useful for template tags, that require
        special syntax or have required arguments.
        It tests for :class:`~django.test.TemplateSyntaxError`, so if your
        template tag raises a custom exception, it should derive from that
        exception.
        Wraps :meth:`unittest.TestCase.assertRaises` and should be used in
        the same way::

            def test_wrong_endtag(self):
                with self.assertSyntaxError():
                    self.renderTemplate('syntax-error.html')

        The positional and keyword arguments are for all intents and purposes
        unused.

        :raises AssertionError: if no TemplateSyntaxError is raised.
        """
        context = AssertRaisesContext(TemplateSyntaxError, self)
        return context.handle('assertSyntaxError', args, kwargs)


class TemplateTestCase(TemplateTestBase, SimpleTestCase):
    __doc__ = """
    Test case for template output

    Provides a simplified way to test templates, adding 3 assertions and a
    way to save the rendered output.

    The class makes use of a template test directory below which the
    following directories should be created:

    `src`
        Source template files. The template code to be tested.

    `expect`
        Expected output files. The expected output of the template after
        rendering. The filenames should correspond with the source templates.

    `actual`
        Actual output files. This directory is created automatically given
        sufficient permissions. The output of the rendered template is saved
        to a file with the same name as the source template if so requested.

    The test case makes use of :class:`~.TemplateContextMixin` and the
    template is
    always rendered using it's :meth:`TemplateContextMixin.get_context`
    method. If you need a
    different way, override the :meth:`~TemplateTestBase.render_template`
    method.
    """


class TemplateWithDbTestCase(TemplateTestBase, DjangoTestCase):
    __doc__ = """
    Test case for template output where database access is required

    Identical to `TemplateTestCase` except that it inherits from Django's
    :class:`~django.test.TestCase`, instead of
    :class:`~django.test.SimpleTestCase`.
    It's primary use case is to test templates that include a widget that
    fetches data from a model, like a standardized country or timezone selector.
    """
