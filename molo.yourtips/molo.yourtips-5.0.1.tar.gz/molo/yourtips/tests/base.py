from django.test import TestCase, Client
from django.contrib.auth.models import User

from molo.core.tests.base import MoloTestCaseMixin
from molo.core.models import (
    SiteLanguageRelation,
    Languages,
    Main
)

from molo.yourtips.models import (
    YourTip, YourTipsIndexPage, YourTipsSectionIndexPage
)


class BaseYourTipsTestCase(TestCase, MoloTestCaseMixin):
    def setUp(self):
        self.mk_main()
        self.language_setting = Languages.objects.create(
            site_id=self.main.get_site().pk)
        self.english = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='en',
            is_active=True)
        self.french = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting,
            locale='fr',
            is_active=True)
        self.user = 'Test'

        # Create tip index page
        self.tip_index = YourTipsIndexPage(title='Your tips', slug='your-tips')
        self.main.add_child(instance=self.tip_index)
        self.tip_index.save_revision().publish()
        self.tip_article_index = YourTipsSectionIndexPage(
            title='Read Tips', slug='read-tips'
        )
        self.tip_index.add_child(instance=self.tip_article_index)
        self.tip_article_index.save_revision().publish()

        self.tip_page = YourTip(
            title='Tip Page',
            description='This is the description',
            slug='tip-page')
        self.tip_index.add_child(instance=self.tip_page)
        self.tip_page.save_revision().publish()

        self.superuser_name = 'test_superuser'
        self.superuser_password = 'password'
        self.superuser = User.objects.create_superuser(
            username=self.superuser_name,
            email='admin@example.com',
            password=self.superuser_password,
            is_staff=True)
        self.client = Client()

        self.mk_main2()
        self.main2 = Main.objects.all().last()
        self.language_setting2 = Languages.objects.create(
            site_id=self.main2.get_site().pk)
        self.english2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='en',
            is_active=True)
        self.french2 = SiteLanguageRelation.objects.create(
            language_setting=self.language_setting2,
            locale='fr',
            is_active=True)

        self.tip_index_main2 = (
            YourTipsIndexPage.objects.child_of(self.main2).first()
        )

        self.client2 = Client(HTTP_HOST=self.main2.get_site().hostname)
