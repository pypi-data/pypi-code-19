import datetime

from molo.yourtips.models import (
    YourTip, YourTipsEntry, YourTipsArticlePage
)
from molo.yourtips.tests.base import BaseYourTipsTestCase


class TestWagtailAdminActions(BaseYourTipsTestCase):

    def test_export_entry_csv(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        tip_page = YourTip(
            title='Test Tip',
            description='This is the description',
            slug='test-tip')
        self.tip_index.add_child(instance=tip_page)
        tip_page.save_revision().publish()

        YourTipsEntry.objects.create(
            optional_name='Test',
            tip_text='test body',
            allow_share_on_social_media=True,
        )

        response = self.client.post('/admin/yourtips/yourtipsentry/')
        date = str(datetime.datetime.now().date())
        expected_output = (
            'Content-Disposition: attachment; filename=yourtips_entries.csv'
            '\r\nContent-Language: en\r\nVary: Accept-Language, Cookie\r\n'
            'Cache-Control: no-cache, no-store, private, max-age=0\r\n'
            'X-Frame-Options: SAMEORIGIN\r\nContent-Type: csv\r\n\r\nid,'
            'submission_date,optional_name,user,tip_text,'
            'allow_share_on_social_media,converted_article_page\r\n1,' +
            date + ',Test,,test body,1,\r\n')
        self.assertEquals(str(response), expected_output)

    def test_export_article_page_csv(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        tip_page = YourTip(
            title='Test Tip',
            description='This is the description',
            slug='test-tip')
        self.tip_index.add_child(instance=tip_page)
        tip_page.save_revision().publish()

        entry = YourTipsEntry.objects.create(
            optional_name='Test',
            tip_text='test body',
            allow_share_on_social_media=True,
        )
        self.client.get(
            '/django-admin/yourtips/yourtipsentry/%d/convert/' % entry.id
        )
        article = YourTipsArticlePage.objects.get(title='Tip-%s' % entry.id)
        article.save_revision().publish()

        response = self.client.post('/admin/yourtips/yourtipsarticlepage/')

        expected_output = (
            'Tip-1,1,test body,Test')
        self.assertContains(response, expected_output)
