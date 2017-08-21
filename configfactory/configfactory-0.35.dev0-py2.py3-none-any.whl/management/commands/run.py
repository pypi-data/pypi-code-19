import multiprocessing
from multiprocessing import Process

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

from configfactory import scheduler, wsgi
from configfactory.support import config
from configfactory.support.server import GunicornServer


class Command(BaseCommand):

    help = 'Run Config Factory application.'

    def add_arguments(self, parser):

        super().add_arguments(parser)

        parser.add_argument(
            '--bind',
            dest='bind',
            default='{host}:{port}'.format(
                host=config.get('server.host', '127.0.0.1'),
                port=config.get('server.port', 8080)
            ),
            help='The socket to bind.',
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            dest='debug',
            default=False,
            help='Use debug.',
        )

    def handle(self, *args, **options):

        # Create configuration file
        if config.is_default:
            config_dst, created = config.create()
            self.stdout.write(
                'ConfigFactory config `{dist}` successfully created.'.format(
                    dist=config_dst
                )
            )

        # Set debug mode
        debug = options['debug']

        # Set settings
        settings.DEBUG = debug

        # Migrate database
        call_command('migrate')

        # Create super user
        # if User.objects.count() == 0:
        #     call_command('createsuperuser')

        # Set server options
        options.update({
            'proc_name': 'configfactory',
        })

        # Set default debug options
        if debug:
            options['reload'] = True
        else:
            options['workers'] = multiprocessing.cpu_count() * 2 + 1

        # Initialize wsgi application
        server = GunicornServer(
            wsgi_app=wsgi.application,
            options=options
        )

        # Create wsgi application process
        server_process = Process(target=server.run)
        server_process.start()

        # Create and start cron application process
        scheduler_process = Process(target=scheduler.run)
        scheduler_process.start()

        # Run multiple processes
        try:
            server_process.join()
            scheduler_process.join()
        except (KeyboardInterrupt, SystemExit):
            print('Shot down signal received...')
