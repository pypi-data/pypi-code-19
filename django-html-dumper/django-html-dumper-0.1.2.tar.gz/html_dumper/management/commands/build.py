import os

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.test.client import Client
from django.utils.translation import activate


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

        output_dir = settings.get(
            settings.SITE_OUTPUT_DIRECTORY,
            'HTML_OUTPUT'
        )

        if not os.path.exists(output_dir):
            os.mkdir(output_dir)

        os.makedirs(settings.STATIC_ROOT)

        call_command(
            'collectstatic', interactive=False, clear=True, verbosity=0)
        client = Client()

        responses = []
        invalid = []
        for url in urls:
            for (code, lang) in settings.LANGUAGES:
                activate(code)
                try:
                    responses.append((url, code, client.get(url)))
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
