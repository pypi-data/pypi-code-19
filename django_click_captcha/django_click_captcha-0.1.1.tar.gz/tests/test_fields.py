from django.core.cache import cache
from django.forms import ValidationError
from django.test import SimpleTestCase

from click_captcha.fields import CaptchaField


class CaptchaWidgetTest(SimpleTestCase):
    def test_field_invalid(self):
        f = CaptchaField()

        # 验证码字段提交为空的情况
        with self.assertRaisesMessage(ValidationError, "'Error verifying input, please try again.'"):
            f.clean(None)

        with self.assertRaisesMessage(ValidationError, "'Error verifying input, please try again.'"):
            f.clean('')
        # 验证码有两个字段
        with self.assertRaisesMessage(ValidationError, "'Error verifying input, please try again.'"):
            f.clean(['123'])

        # 验证码的格式不对
        with self.assertRaisesMessage(ValidationError, "'Error verifying input, please try again.'"):
            f.clean(['123', '123'])

        # 后台没有该验证码
        with self.assertRaisesMessage(ValidationError, "'captcha has expired, please refresh and try again'"):
            f.clean(['123', '12,12'])

        cache.set('123', ([0], 10, 12))

        # 校验的验证码不一致， 点击的不是倒字
        with self.assertRaisesMessage(ValidationError, "'Incorrect, please try again.'"):
            f.clean(['123', '11, 10'])

        # 校验的验证码不一致， 点击的位置不在图片的高度范围内
        with self.assertRaisesMessage(ValidationError, "'Incorrect, please try again.'"):
            f.clean(['123', '9, 13'])

        # 点击的倒字数目多， 但匹配的情况
        with self.assertRaisesMessage(ValidationError, "'Incorrect, please try again.'"):
            f.clean(['123', '9,10,8,8'])

    def test_field_valid(self):
        f = CaptchaField()
        cache.set('abc', ([0], 10, 12))
        self.assertEqual(f.clean(['abc', '9,10']), [0])

    def test_field_valid_more(self):
        f = CaptchaField()
        cache.set('xyz', ([0, 50, 100], 50, 60))
        self.assertEqual(f.clean(['xyz', '34.5,50,53,49.123,101,12']), [0, 50, 100])

    def test_widget_render(self):
        f = CaptchaField(click_captcha_id='captcha_id', click_captcha_value='captcha',
                         captcha_cache_key_gen_func=lambda: 'abc')
        output = f.widget.render('', '')
        self.assertInHTML('<input type="hidden" name="captcha" class="captcha-field">', output)
        self.assertInHTML('<input type="hidden" name="captcha_id" value="abc">', output)
