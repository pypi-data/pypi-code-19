import logging

from flasky import events, handler
from flasky.handler import RequestContext
from quark_utilities import temporal_helpers, db

logger = logging.getLogger('WebhookListener')

class WebhookListener(object):

    def __init__(self, app):
        self._app = app

    async def on_event(self, event):
        webhooks_repository = await self._app.di.get('webhooks_repository')
        webhook_queue_repository = await self._app.di.get('webhook_queue_repository')
        cid_generator = self._app.di.cid_generator

        if not hasattr(event, 'domain_id'):
            logger.info(
                'Event<{}, {}> has no domainID, Passing event'.format(
                    event._id, event.type))

            return

        where = {
                'domain_id': event.domain_id,
                'event_type': event.type
        }

        webhook_definitions, count= await webhooks_repository.query(
            where=where
        )

        if not webhook_definitions:
            logger.info('There is no Webhook Defination in Repository')

            return

        for webhook_definition in webhook_definitions:
            webhook_record = {
                '_id' : db.create_id(),
                'event_id': str(event._id),
                'domain_id': event.domain_id,
                'webhook_id': str(webhook_definition['_id']),
                'status' : 'PENDING',
                'sys': {
                    'created_at': temporal_helpers.utc_now(),
                    'created_by': event.token['prn'],
                    'cid': (await cid_generator.generate('webhook_queue'))
                }}

            await webhook_queue_repository.save(webhook_record)

            logger.info('Webhook<_id:{}, event_type:{}, webhook_definition_id:{}> '
                        'successfuly saved to Webhooks Queue'.format(
                webhook_record['_id'],
                event.type, webhook_record['webhook_id']))

