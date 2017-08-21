import logging

from celery import Celery

from kore.components.plugins.base import BasePluginComponent

log = logging.getLogger(__name__)


class CeleryPluginComponent(BasePluginComponent):

    def get_services(self):
        return (
            ('config', self.config),
        )

    def pre_hook(self, container):
        if 'kore.components.celery.application' in container:
            return

        container['kore.components.celery.application'] = Celery()

    def config(self, container):
        config = container('config')

        return config.get('celery', {})

    def post_hook(self, container):
        app = container('kore.components.celery.application')
        config = container('kore.components.celery.config')

        app.main = config.get('main', 'kore-celery-app')
        broker_url = config.get('broker_url', 'amqp://')
        result_backend = config.get('result_backend', None)
        task_serializer = config.get('task_serializer', 'json')
        result_serializer = config.get('result_serializer', 'json')
        timezone = config.get('timezone', 'UTC')
        worker_hijack_root_logger = config.get(
            'worker_hijack_root_logger', False)

        app.conf.update(
            broker_url=broker_url,
            result_backend=result_backend,
            task_serializer=task_serializer,
            result_serializer=result_serializer,
            timezone=timezone,
            worker_hijack_root_logger=worker_hijack_root_logger,
        )
