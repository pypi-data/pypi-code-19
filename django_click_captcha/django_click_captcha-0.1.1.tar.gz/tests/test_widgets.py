from unittest.mock import patch

from django.test import SimpleTestCase

from click_captcha.widgets import Captcha


class CaptchaWidgetTest(SimpleTestCase):
    def test_render_default(self):
        widget = Captcha()
        output = widget.render('', '')
        self.assertInHTML('<input type="hidden" name="click_captcha_value" class="captcha-field">', output)

    def test_render(self):
        with patch.object(Captcha, 'captcha_cache_key_gen', lambda self: 'abc'):
            widget = Captcha()
            widget.click_captcha_value = 'captcha'
            widget.click_captcha_id = 'captcha_id'
            output = widget.render('', '')
            self.assertInHTML('<input type="hidden" name="captcha" class="captcha-field">', output)
            self.assertInHTML('<input type="hidden" name="captcha_id" value="abc">', output)
