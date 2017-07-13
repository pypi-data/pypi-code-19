from django.template import Template, Context

from molo.yourtips.models import (
    YourTipsEntry, YourTipsArticlePage
)
from molo.yourtips.tests.base import BaseYourTipsTestCase


class TestYourTipsTemplateTags(BaseYourTipsTestCase):

    def test_your_tips_on_homepage(self):
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

        template = Template("""
        {% load tip_tags %}
        {% your_tips_on_homepage %}
        """)

        output = template.render(Context({
            'object': self.user,
        }))

        self.assertTrue('test body' in output)

    def test_your_tips_on_tip_submission_form(self):
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

        template = Template("""
        {% load tip_tags %}
        {% your_tips_on_tip_submission_form %}
        """)

        output = template.render(Context())

        self.assertTrue('test body' in output)
