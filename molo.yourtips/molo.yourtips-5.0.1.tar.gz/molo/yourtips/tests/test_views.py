from django.core.urlresolvers import reverse

from molo.yourtips.tests.base import BaseYourTipsTestCase
from molo.yourtips.models import (
    YourTipsEntry, YourTipsArticlePage
)


class TestYourTipsViewsTestCase(BaseYourTipsTestCase):
    def test_yourtips_page(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        response = self.client.get(self.tip_page.url)
        self.assertContains(response, 'Tip Page')

    def test_yourtips_thank_you_page(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        response = self.client.post(
            reverse('molo.yourtips:tip_entry', args=[self.tip_page.slug]), {
                'tip_text': 'The text',
                'allow_share_on_social_media': 'true'})
        self.assertEqual(
            response['Location'],
            '/yourtips/thankyou/tip-page/')

    def test_yourtips_recent_tip_view(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

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

        response = self.client.get(reverse('molo.yourtips:recent_tips'))
        self.assertContains(response, 'Test')
        self.assertContains(response, 'test body')

    def test_yourtips_popular_tip_view(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        entry = YourTipsEntry.objects.create(
            optional_name='Test',
            tip_text='test body',
            allow_share_on_social_media=True,
        )

        self.client.get(
            '/django-admin/yourtips/yourtipsentry/%d/convert/' % entry.id
        )
        article = YourTipsArticlePage.objects.get(title='Tip-%s' % entry.id)
        article.add_vote('1.2.3.4', 1)
        article.save_revision().publish()

        response = self.client.get(reverse('molo.yourtips:popular_tips'))
        self.assertContains(response, 'Test')
        self.assertContains(response, 'test body')
