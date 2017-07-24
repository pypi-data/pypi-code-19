from django.core.urlresolvers import reverse

from molo.yourtips.tests.base import BaseYourTipsTestCase
from molo.yourtips.models import (
    YourTip, YourTipsEntry, YourTipsArticlePage
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

    def test_yourtips_form_and_validation_for_fields(self):
        self.client.login(
            username=self.superuser_name,
            password=self.superuser_password
        )

        tip_page = YourTip.objects.get(slug='tip-page')

        self.client.get(
            reverse('molo.yourtips:tip_entry', args=[tip_page.slug]))

        response = self.client.post(
            reverse('molo.yourtips:tip_entry', args=[tip_page.slug]), {})
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'This field is required')

        response = self.client.post(
            reverse('molo.yourtips:tip_entry', args=[tip_page.slug]),
            {
                'tip_text': 'This is a very long story _7 _8 _9 10 11 12 13 '
                            '14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 '
                            '29 30 31',
                'allow_share_on_social_media': 'true'
            })
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Sorry your tip is too long, please edit'
                                      ' it and cut down 1 words.')

        response = self.client.post(
            reverse('molo.yourtips:tip_entry', args=[tip_page.slug]),
            {
                'tip_text': 'This_is_a_very_long_story_single_string_________'
                            '________________________________________________'
                            '________________________________________________',
                'allow_share_on_social_media': 'true'
            })
        self.assertEquals(response.status_code, 200)
        self.assertContains(response, 'Sorry your tip is too long, please edit'
                                      ' it and cut down 4 characters.')

        response = self.client.post(
            reverse('molo.yourtips:tip_entry', args=[tip_page.slug]),
            {
                'tip_text': 'This is a correct tip ',
                'allow_share_on_social_media': 'true'
            })
        self.assertEquals(response.status_code, 302)
        self.assertEquals(YourTipsEntry.objects.all().count(), 1)
