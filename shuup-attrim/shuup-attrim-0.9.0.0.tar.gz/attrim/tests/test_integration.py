from unittest import skipIf

from django.contrib.auth import get_user_model
from shuup.testing.factories import get_default_tax_class
from shuup_testutils.cases import IntegrationTestCase

from attrim.apps import AppConfig
from attrim.models import Option
from attrim.testutils.generators import ModelsGen
from attrim.models.type import Type
from attrim.trans_str import TransStr
from attrim.tests.workbench.settings import IS_SHUUP_TEST_LOCAL


class IntegrationTest(IntegrationTestCase):
    python_module_name = AppConfig.name
    yarn_dir = 'static/{}/admin'.format(AppConfig.name)
    protractor_conf = 'protractor.conf.js'
    server_address = 'localhost:8082'

    @classmethod
    def set_up_class_after(cls):
        super().set_up_class_after()
        cls._gen_mock_data()

    @skipIf(IS_SHUUP_TEST_LOCAL == False, 'It does not work in the CI yet.')
    def test_integration(self):
        super().run_protractor_tests()

    @classmethod
    def _gen_mock_data(cls):
        get_user_model().objects.create_superuser(
            username='test',
            email='test@localhost',
            password='test@localhost',
        )

        get_default_tax_class()

        gen = ModelsGen()
        gen.product()

        cls_lang = gen.attrim.cls(
            code='language',
            name=TransStr(
                en='Translations',
                fi='Translations fi',
            ),
            type=Type.TRANS_STR,
            options_amount=0,
        )
        Option.objects.create(cls=cls_lang, value=TransStr(en='english'), order=1)
        Option.objects.create(cls=cls_lang, value=TransStr(en='german'), order=2)
        Option.objects.create(cls=cls_lang, value=TransStr(en='finish'), order=3)
