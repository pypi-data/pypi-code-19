from django.core.management.base import BaseCommand
from viewed_models import ViewDefinition
import logging
logger = logging.getLogger(__name__)

REVISION = 2  # Increment this to determine where in the migrations run the views ought to be (re-)created


class Command(BaseCommand):
    help = 'Recreates the views found in aims viewed_models'

    def add_arguments(self, parser):
        parser.add_argument('--revision', default='1', help='The revision number to run')
        parser.add_argument('--apps', default='all', help='Comma separated list of apps to rebuild views in')

    def handle(self, *args, **options):

        def enabled():
            """
            Check that the revision number matches - this prevents code from a newer views schema
            being run against old tables
            """
            return str(REVISION) == str(options['revision'])

        if enabled():
            logger.info('Regenerating views.')
            ViewDefinition.recreate(apps=str(options['apps']))
        else:
            w = 'Command revision {} != file revision {}. No views will be regenerated.'.format(options['revision'], REVISION)
            logger.info(w)
