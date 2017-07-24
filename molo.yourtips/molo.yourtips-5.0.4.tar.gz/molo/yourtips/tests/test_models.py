from molo.core.tests.base import MoloTestCaseMixin

from molo.yourtips.models import (
    YourTip, YourTipsEntry, YourTipsArticlePage
)
from molo.yourtips.tests.base import BaseYourTipsTestCase


class TestYourTipsModels(BaseYourTipsTestCase, MoloTestCaseMixin):

    def test_get_number_of_tips(self):
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

        self.assertEquals(YourTip.get_number_of_tips(), 0)
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

        self.assertEquals(YourTip.get_number_of_tips(), 1)

    def test_get_number_of_popular_tips(self):
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
        self.assertEquals(YourTip.get_number_of_popular_tips(), 0)
        article.add_vote('1.2.3.4', 1)
        self.assertEquals(YourTip.get_number_of_popular_tips(), 1)
