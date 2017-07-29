from django.test import TestCase

#from django.conf import settings
from django.utils.safestring import mark_safe

from countable_field import widgets


HTML_TEMPLATE = (
    '<textarea name="countable" cols="40" rows="10" data-min-count="%(min_count)s" data-max-count="%(max_count)s">\n'
    '</textarea>'
    '<span class="text-count" id="None_counter">Word count:'
    '<span class="text-count-current">0</span></span>\r\n'
    '<script type="text/javascript">var countableField = new CountableField("None")</script>\n'
)


class WidgetTestCase(TestCase):

    # def setUp(self):
    #     settings.configure()

    def test_no_limits(self):
        widget = widgets.CountableWidget()
        result = widget.render('countable', None)
        self.assertTrue(str(result).__contains__('data-min-count="false"'))
        self.assertTrue(str(result).__contains__('data-max-count="false"'))

    def test_lower_limit(self):
        widget = widgets.CountableWidget()
        result = widget.render('countable', None, attrs={'data-min-count': 50})
        self.assertTrue(str(result).__contains__('data-min-count="50"'))
        self.assertTrue(str(result).__contains__('data-max-count="false"'))

    def test_upper_limit(self):
        widget = widgets.CountableWidget()
        result = widget.render('countable', None, attrs={'data-max-count': 70})
        self.assertTrue(str(result).__contains__('data-min-count="false"'))
        self.assertTrue(str(result).__contains__('data-max-count="70"'))

    def test_both_limits(self):
        widget = widgets.CountableWidget()
        result = widget.render('countable', None, attrs={'data-min-count': 30, 'data-max-count': 80})
        self.assertTrue(str(result).__contains__('data-min-count="30"'))
        self.assertTrue(str(result).__contains__('data-max-count="80"'))

    def test_invalid_limits(self):
        widget = widgets.CountableWidget()
        result = widget.render('countable', None, attrs={'data-min-count': 'blue', 'data-max-count': 50.9})
        self.assertTrue(str(result).__contains__('data-min-count="false"'))
        self.assertTrue(str(result).__contains__('data-max-count="false"'))
