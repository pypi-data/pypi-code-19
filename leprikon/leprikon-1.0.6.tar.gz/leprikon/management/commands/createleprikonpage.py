# -*- coding: utf-8 -*-
from cms.api import create_page
from cms.constants import TEMPLATE_INHERITANCE_MAGIC
from django.core.management.base import BaseCommand, CommandError
from menus.menu_pool import menu_pool

from ...conf import settings


class Command(BaseCommand):
    help = 'Creates Leprikon page'

    def add_arguments(self, parser):
        parser.add_argument('title', nargs='?', default='Leprikón')
        parser.add_argument('slug', nargs='?', default='leprikon')

    def handle(self, *args, **options):
        # create cms page with Leprikon apphook
        create_page(
            title=options['title'],
            template=TEMPLATE_INHERITANCE_MAGIC,
            language=settings.LANGUAGE_CODE,
            slug=options['slug'],
            apphook='LeprikonApp',
            apphook_namespace='leprikon',
            reverse_id='leprikon',
            navigation_extenders='LeprikonMenu',
            published=True,
        )
        # clear menus cache
        menu_pool.clear()
