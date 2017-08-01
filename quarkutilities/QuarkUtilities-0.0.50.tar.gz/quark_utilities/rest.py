import copy
import os

import logging

from flasky import events
from flasky.handler import RequestContext
from quark_utilities import query_helpers

from quark_utilities import errors
from quark_utilities import responser
from quark_utilities import temporal_helpers

class GenericService(object):

    def __init__(self, repository):
        self.repository = repository

    async def query(self, where=None, select=None, skip=None, limit=None, sort=None):
        domain_id = RequestContext.get_param('domain_id')

        where.update({
            'domain_id': domain_id
        })

        content, counts = await self.repository.query(
            where=where,
            select=select,
            skip=skip,
            limit=limit,
            sort=sort
        )

        return (content, counts)

class GenericMembershipEntityService(GenericService):

    def __init__(self, repository):
        super(GenericMembershipEntityService, self).__init__(repository)




class GenericDomainEntityService(object):

    def __init__(self):
        pass

    async def create(self, data):
        pass

    async def find(self, resource_id):
        pass

    async def delete(self, resource_id):
        pass

    async def update(self, resource_id):
        pass


class GenericResource(object):

    def __init__(self, resource_name, api_prefix=None, collection_name=None,
                 event_name_prefix=None, create_json_schema=None,
                 update_json_schema=None, allowed_ops=None, before_create=None,
                 after_create=None, before_update=None, after_update=None,
                 before_delete=None, after_delete=None):

        self.api_prefix = api_prefix
        self.resource_name = resource_name
        self.event_name_prefix = event_name_prefix
        self.collection_name = collection_name
        self.allowed_ops = allowed_ops or ['CREATE', 'UPDATE', 'READ', 'DELETE', 'QUERY']

        self.logger = logging.getLogger('resource.' + self.resource_name + '.logger')

        #: Json Schemas
        self._create_json_schema = create_json_schema
        self._update_json_schema = update_json_schema

        #: Hooks
        self._before_create = before_create or []
        self._after_create = after_create or []
        self._before_update = before_update or []
        self._after_update = after_update or []
        self._after_delete = after_delete or []
        self._before_delete = before_delete or []

    def before_create(self, f):
        self._before_create.append(f)
        return f

    def resolve_url(self, url=None):
        resolved = os.path.join('/', self.api_prefix or '', self.resource_name, url or '')

        if resolved.endswith('/'):
            return resolved[:-1]

        return resolved

    @property
    def repository_name(self):
        return self.collection_name + '_repository'

    async def repository(self):
        return await RequestContext.current_app().di.get(self.repository_name)

    def resolve_event_name(self, event_type):
        if event_type == 'create':
            return self.event_name_prefix + 'CreatedEvent'
        elif event_type == 'update':
            return self.event_name_prefix + 'UpdatedEvent'
        elif event_type == 'delete':
            return self.event_name_prefix + 'DeletedEvent'
        else:
            raise errors.QError(
                err_msg='Unsupported event type<{}>'.format(event_type),
                err_code='errors.internalError'
            )

    async def __run_function_pool(self,handler, func_pool, **kwargs):
        document = kwargs.get('resource', None)
        if not document:
            raise errors.FError(
                err_msg='Internal error occured...',
                err_code='errors.internalError',
                status_code=500
            )

        for func in func_pool:
            document = await handler.di.inject_and_run(func, **kwargs)

        return document

    async def create(self, handler, *args, **kwargs):
        domain_id = args[0]
        subject = RequestContext.current_data()['subject']

        resource = handler.body_as_json()

        resource.update({
            'domain_id': domain_id,
            'membership_id': subject.membership_id,
            'sys': {
                'created_at': temporal_helpers.utc_now(),
                'created_by': subject.token['prn'],
                'cid': (await handler.di.cid_generator.generate(self.collection_name)),
                'version': 1
            }
        })

        repository = await handler.di.get(self.repository_name)

        resource = await self.__run_function_pool(
            handler,
            self._before_create,
            resource=resource
        )

        saved = await repository.save(resource)

        resource = await self.__run_function_pool(
            handler,
            self._after_create,
            resource=resource
        )

        await events.dispatch(events.Event(
            type=self.resolve_event_name('create'),
            document=resource,
            domain_id=domain_id,
            token=subject.token,
            sys={
                'created_at': temporal_helpers.utc_now(),
                'created_by': 'system'
            }
        ))

        responser.to_response(
            handler,
            201,
            documents=saved
        )

    async def query(self, handler, *args, **kwargs):
        domain_id = args[0]

        where, select, limit, sort, skip = query_helpers.parse(handler)

        repository = await handler.di.get(self.repository_name)

        where.update({
            'domain_id': domain_id
        })

        contents, total_count = await repository.query(
            where=where,
            select=select,
            skip=skip,
            limit=limit,
            sort=sort
        )

        responser.to_response(
            handler,
            200,
            documents=contents,
            count=total_count
        )


    async def get(self, handler, *args, **kwargs):
        domain_id, content_id = args[0], args[1]

        repository = await self.repository()

        resource = await repository.find_one_by(where={
            '_id': content_id,
            'domain_id': domain_id
        })

        responser.to_response(
            handler,
            200,
            documents=resource
        )

    async def update(self, handler, *args, **kwargs):
        domain_id, resource_id, subject = args[0], args[1], RequestContext.get_param('subject')

        repository = await self.repository()

        resource = await repository.find_one_by(
          where={
              '_id': resource_id,
              'domain_id': domain_id
          }
        )

        _resource = copy.deepcopy(resource)

        extra_data = handler.body_as_json()
        extra_data.pop('sys', None)
        extra_data.pop('membership_id', None)
        extra_data.pop('domain_id', None)
        extra_data.pop('_id', None)

        resource.update(extra_data)
        resource['sys'].update({
            'modified_at': temporal_helpers.utc_now(),
            'modified_by': subject.token['prn'],
            'version': resource['sys'].get('version', 1) + 1
        })

        resource = await self.__run_function_pool(
            handler,
            self._before_update,
            resource=resource,
            _resource=_resource
        )

        await repository.replace(resource)

        resource = await self.__run_function_pool(
            handler,
            self._after_update,
            resource=resource,
            _resource=_resource
        )

        await events.dispatch(
            events.Event(
                type=self.resolve_event_name('update'),
                prior=_resource,
                document=resource,
                user=subject.token,
                domain_id=domain_id
            )
        )

        responser.to_response(
            handler,
            200,
            documents=resource
        )

    async def delete(self, handler, *args, **kwargs):
        domain_id, resource_id = args[0], args[1]
        subject = RequestContext.get_param('subject')

        repository = await handler.di.get(self.repository_name)

        document_query = {
            '_id': resource_id,
            'domain_id': domain_id
        }

        resource = await repository.find_one_by(where=document_query)

        resource = await self.__run_function_pool(
            handler,
            self._before_delete,
            resource=resource
        )

        await repository.remove_one_by(
            where={
                '_id': resource_id,
                'domain_id': domain_id
            }
        )

        resource = await self.__run_function_pool(
            handler,
            self._after_delete,
            resource=resource
        )

        await events.dispatch(
            events.Event(
                type=self.resolve_event_name('delete'),
                document=resource,
                user=subject.token
            )
        )

        responser.to_response(
            handler,
            204
        )

    def register(self, app):
        self.logger.info("Resource initialized on <{}> URL".format(self.resolve_url()))

        if 'CREATE' in self.allowed_ops:
            if self._create_json_schema:
                @app.api(
                    endpoint=self.resolve_url(),
                    method='POST',
                    json_schema=self._create_json_schema
                )
                async def create_resource(handler, *args, **kwargs):
                    await self.create(handler, *args, **kwargs)
            else:
                @app.api(
                    endpoint=self.resolve_url(),
                    method='POST'
                )
                async def create_resource(handler, *args, **kwargs):
                    await self.create(handler, *args, **kwargs)

        if 'QUERY' in self.allowed_ops:
            @app.api(
                endpoint=self.resolve_url('_query'),
                method='POST'
            )
            async def query_resource(handler, *args, **kwargs):
                await self.query(handler, *args, **kwargs)

        if 'READ' in self.allowed_ops:
            @app.api(
                endpoint=self.resolve_url('([^/]+)'),
                method='GET'
            )
            async def read_resource(handler, *args, **kwargs):
                await self.get(handler, *args, **kwargs)


        if 'UPDATE'in self.allowed_ops:
            if self._update_json_schema:
                @app.api(
                    endpoint=self.resolve_url('([^/]+)'),
                    method='PUT',
                    json_schema=self._update_json_schema
                )
                async def update_resource(handler, *args, **kwargs):
                    await self.update(handler, *args, **kwargs)
            else:
                @app.api(
                    endpoint=self.resolve_url('([^/]+)'),
                    method='PUT',
                )
                async def update_resource(handler, *args, **kwargs):
                    await self.update(handler, *args, **kwargs)

        if 'DELETE' in self.allowed_ops:
            @app.api(
                endpoint=self.resolve_url('([^/]+)'),
                method='DELETE'
            )
            async def delete_resource(handler, *args, **kwargs):
                await self.delete(handler, *args, **kwargs)


