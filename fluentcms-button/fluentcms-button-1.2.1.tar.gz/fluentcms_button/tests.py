from django.test import TestCase
from fluent_contents.tests.factories import create_content_item
from fluent_contents.tests.utils import render_content_items
from fluentcms_button.models import ButtonItem


class ButtonTests(TestCase):
    """
    Testing private notes
    """

    def test_primary(self):
        """
        Test the standard button
        """
        item = create_content_item(ButtonItem, url='http://example.com', style='btn-primary', title='TEST')
        self.assertHTMLEqual(render_content_items([item]).html, u'<a href="http://example.com" class="btn btn-primary">TEST</a>')

    def test_align_center(self):
        """
        Test the center-align feature.
        """
        item = create_content_item(ButtonItem, url='http://example.com', style='btn-default', title='TEST2', align='center')
        self.assertHTMLEqual(
            render_content_items([item]).html,
            u'<p class="text-center btn-center-wrapper"><a href="http://example.com" class="btn btn-default">TEST2</a></p>'
        )
