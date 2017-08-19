from unittest import TestCase

from bs4 import BeautifulSoup

from trunity_migrator.fixers import *


class FixersTestCase(TestCase):

    def test_fix_img_src(self):
        html = '''
        <h1>Hi dude!</h1>
        <p>
            <img alt="" src="/path/to/files/image1.jpg" style="width: 318px; height: 217px;" />
        </p>
        '''

        base_url = 'http://www.trunity.net'

        expected_html = '''
        <h1>Hi dude!</h1>
        <p>
            <img alt="" src="http://www.trunity.net/path/to/files/image1.jpg" style="width: 318px; height: 217px;" />
        </p>
        '''

        result_html = fix_img_src(html, base_url)

        # we use BeautifulSoup to compare html:
        self.assertEqual(
            BeautifulSoup(result_html, "html.parser"),
            BeautifulSoup(expected_html, "html.parser"),
            'html and expected_html are not equal!'
        )

    def test_fix_table_width(self):
        html = '''
        <h2>Change width from 766 to 100%</h2>
        <table border="0" cellpadding="0" cellspacing="0" height="36" style="background-color: rgb(191, 242, 255);" width="766">
            <tbody>
                <tr>
                    <td style="width: 712px;"><strong>The structure of DNA</strong></td>
                    <td style="width: 20px;">&nbsp;</td>
                </tr>
            </tbody>
        </table>
        
        <h2>Change width from 770 to 70%</h2>
        <table border="0" cellpadding="0" cellspacing="0" height="36" style="background-color: rgb(191, 242, 255);" width="770">
            <tbody>
                <tr>
                    <td style="width: 712px;"><strong>The structure of DNA</strong></td>
                    <td style="width: 20px;">&nbsp;</td>
                </tr>
            </tbody>
        </table>
        '''

        expected_html = '''
        <h2>Change width from 766 to 100%</h2>
        <table border="0" cellpadding="0" cellspacing="0" height="36" style="background-color: rgb(191, 242, 255);" width="100%">
            <tbody>
                <tr>
                    <td style="width: 712px;"><strong>The structure of DNA</strong></td>
                    <td style="width: 20px;">&nbsp;</td>
                </tr>
            </tbody>
        </table>

        <h2>Change width from 770 to 70%</h2>
        <table border="0" cellpadding="0" cellspacing="0" height="36" style="background-color: rgb(191, 242, 255);" width="70%">
            <tbody>
                <tr>
                    <td style="width: 712px;"><strong>The structure of DNA</strong></td>
                    <td style="width: 20px;">&nbsp;</td>
                </tr>
            </tbody>
        </table>
        '''

        result_html = fix_table_width(
            html,
            old_widths=["766", "770"],
            new_widths=["100%", "70%"]
        )

        self.assertEqual(
            BeautifulSoup(expected_html, "html.parser"),
            BeautifulSoup(result_html, "html.parser"),
            "Result html is not equal to expected!"
        )

        # TODO: try use this: from bs4.testing import SoupTest
        # self.assertSoupEquals