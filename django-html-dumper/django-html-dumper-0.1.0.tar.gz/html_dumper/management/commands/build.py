import errno
import os
import shutil
from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.core.urlresolvers import reverse
from django.test.client import Client


def create_file_and_ancestors(filename):
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc:  # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise


class Command(BaseCommand):
    help = 'Build static site output.'

    def add_arguments(self, parser):
        parser.add_url(
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
        import pdb; pdb.set_trace()
        # if args:
        #     pages = args
        #     available = list(get_pages())
        #     invalid = []
        #     for page in pages:
        #         if page not in available:
        #             invalid.append(page)
        #     if invalid:
        #         msg = 'Invalid pages: {}'.format(', '.join(invalid))
        #         raise CommandError(msg)
        # else:
        #     pages = get_pages()
        #     if os.path.exists(settings.SITE_OUTPUT_DIRECTORY):
        #         shutil.rmtree(settings.SITE_OUTPUT_DIRECTORY)
        #     os.mkdir(settings.SITE_OUTPUT_DIRECTORY)
        #     os.makedirs(settings.STATIC_ROOT)

        # call_command(
        #     'collectstatic', interactive=False, clear=True, verbosity=0)
        # client = Client()

        # for page in pages:
        #     url = reverse('page', kwargs={'slug': page})
        #     response = client.get(url)
        #     if page == 'index':
        #         output_dir = settings.SITE_OUTPUT_DIRECTORY
        #     else:
        #         output_dir = os.path.join(settings.SITE_OUTPUT_DIRECTORY, page)
        #         os.makedirs(output_dir)
        #     with open(os.path.join(output_dir, 'index.html'), 'wb') as f:
        #         f.write(response.content)
