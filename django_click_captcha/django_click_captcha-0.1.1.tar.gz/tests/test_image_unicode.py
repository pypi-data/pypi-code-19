import os
import unittest
from unittest.mock import patch

from click_captcha.image_unicode import gb2312, ImageChar


class RandomGB2312Test(unittest.TestCase):
    def test_gb2312(self):
        s = gb2312()
        self.assertEqual(len(s), 1)
        self.assertTrue(isinstance(s, str))


class ImageCharTest(unittest.TestCase):
    current_path = os.path.dirname(__file__)

    def test_random_chinese_default(self):
        with patch.object(ImageChar, 'choice_index', lambda cls, number: [0, 1, 2]):
            i1 = ImageChar()
            point_list, img = i1.random_chinese()
            self.assertEqual([0, 30, 60], point_list)
            # im = Image.open(img)
            self.assertEqual(img.height, 50)
            self.assertTrue(img.width >= 30 * 6)

    def test_random_chinese_no_default(self):
        with patch.object(ImageChar, 'choice_index', lambda cls, number: [4, 5, 6]):
            i1 = ImageChar(font_color=(255, 0, 0), height=60, char_number=7,
                           font_path=os.path.join(self.current_path, 'resource/Vera.ttf'),
                           bg_color=(0, 0, 0, 255), font_size=40)
            point_list, img = i1.random_chinese()
            self.assertEqual([160, 200, 240], point_list)
            self.assertEqual(img.height, 60)
            self.assertTrue(img.width >= 40 * 7)
