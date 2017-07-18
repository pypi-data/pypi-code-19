from django.template import Template, Context
from django.test import TestCase


class IncludeStaticTestCase(TestCase):
    """ Test the {% include_static %} template tag. """

    def setUp(self):
        pass

    def test_resulting_file_includes_static_file(self):
        # Arrange
        template = Template("abc {% load amptags %}{% include_static 'tests/static_file.txt' %} xyz")

        # Act
        rendered = template.render(Context({}))

        # Assert
        self.assertIn("The quick brown fox jumped over the lazy dog.", rendered)

    def test_resulting_file_includes_unescaped_static_file(self):
        # Arrange
        template = Template("abc {% load amptags %}{% include_static 'tests/static_file_with_escapables.txt' %} xyz")

        # Act
        rendered = template.render(Context({}))

        # Assert
        self.assertIn("The \"quick\" brown fox 'jumped' over the <lazy> dog.", rendered)

# TODO: Tests for include_css
# TODO: Tests for AMPPostMiddleware


