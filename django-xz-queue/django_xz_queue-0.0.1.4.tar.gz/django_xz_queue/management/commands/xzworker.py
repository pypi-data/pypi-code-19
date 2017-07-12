import importlib
import sys

from django.core.management.base import BaseCommand
from django_xz_queue.consumer import Worker


class Command(BaseCommand):
    """
    Runs RQ workers on specified queues. Note that all queues passed into a
    single rqworker command must share the same connection.

    Example usage:
    python manage.py rqworker queue_name
    """

    # args = '<queue queue ...>'

    # def add_arguments(self, parser):
    #     parser.add_argument('--worker-class', action='store', dest='worker_class',
    #                         default='rq.Worker', help='RQ Worker class to use')
    #     parser.add_argument('--pid', action='store', dest='pid',
    #                         default=None, help='PID file to write the worker`s pid into')
    #     parser.add_argument('--burst', action='store_true', dest='burst',
    #                         default=False, help='Run worker in burst mode')
    #     parser.add_argument('--name', action='store', dest='name',
    #                         default=None, help='Name of the worker')
    #     parser.add_argument('--queue-class', action='store', dest='queue_class',
    #                         default='django_rq.queues.DjangoRQ', help='Queues class to use')
    #     parser.add_argument('--worker-ttl', action='store', type=int,
    #                         dest='worker_ttl', default=420,
    #                         help='Default worker timeout to be used')
    #     if LooseVersion(get_version()) >= LooseVersion('1.10'):
    #         parser.add_argument('args', nargs='*', type=str,
    #                             help='The queues to work on, separated by space')

    def handle(self, *args, **options):
        try:
            worker = Worker(*args)
            worker.run()
        except Exception as e:
            print(e)
            sys.exit(1)

