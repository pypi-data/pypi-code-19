import os
import shutil

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.test.client import Client
from django.utils import translation


class Command(BaseCommand):
    help = 'Build static site output.'

    def add_arguments(self, parser):
        parser.add_argument(
            'url',
            default=['/', ],
            nargs='*',
            type=str,
            help=(
                'Specify a list of URLs that you want their page to be dumped'
            ),
        )

    def handle(self, *args, **options):
        """Request pages and build output."""
        settings.DEBUG = False
        urls = options['url']

        output_dir = getattr(
            settings,
            'SITE_OUTPUT_DIRECTORY',
            'HTML_OUTPUT'
        )

        static_dir = os.path.join(output_dir, 'static')
        if os.path.exists(static_dir):
            shutil.rmtree(static_dir)

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        if not os.path.exists(settings.STATIC_ROOT):
            os.makedirs(settings.STATIC_ROOT)

        call_command(
            'collectstatic', interactive=False, clear=True, verbosity=0)
        static_dir = os.path.join(output_dir, 'static')
        if os.path.exists(static_dir):
            shutil.rmtree(static_dir)
        shutil.copytree(settings.STATIC_ROOT, static_dir)

        responses = []
        invalid = []
        client = Client()

        for url in urls:
            for (code, lang) in settings.LANGUAGES:
                try:
                    with translation.override(code):
                        client.cookies.load(
                            {settings.LANGUAGE_COOKIE_NAME: code}
                        )
                        responses.append(
                            (
                                url,
                                code,
                                client.get(url, HTTP_ACCEPT_LANGUAGE=code),
                            )
                        )
                except:
                    invalid.append(url)

        if invalid:
            msg = 'Invalid urls: {}'.format(', '.join(invalid))
            raise CommandError(msg)

        for (counter, (url, lang, response)) in enumerate(responses):
            name = url.strip('/').replace('/', '--')
            name = name if name != '' else 'index'
            name = '{}_{}.html'.format(name, lang)
            with open(os.path.join(output_dir, name), 'wb') as f:
                f.write(response.content)
