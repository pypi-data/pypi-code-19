from opfront.exceptions import ResourceNotFoundError
from opfront.model import Model

import json


class OpfrontResource(object):

    """
    OpfrontResource represents an entire resource of the Opfront API (Ex: All stores)

    Args:
        endpoint (str): Endpoint that maps to the resource
        client (OpfrontClient): Authenticated opfront client
    """

    def __init__(self, endpoint, client):
        self._endpoint = endpoint
        self._client = client

    def _make_model(self, **kwargs):
        return Model(self, **kwargs)

    def __call__(self, **kwargs):
        """
        Create a new model instance
        Args:
            **kwargs: Attributes of the model

        Returns:
            Model: Model instance

        """
        return self._make_model(**kwargs)

    def exists(self, res_id):
        """
        Checks if a resource instance exists

        Args:
            res_id: ID of the resource

        Returns:
            bool: Resource exists
        """
        try:
            self.get(res_id)

        except ResourceNotFoundError:
            return False

        else:
            return True

    def get(self, res_id):
        """
        Get a resource instance from ID

        Args:
            res_id: ID of the resource

        Returns:
            Model: Resource instance
        """

        res_url = '{endpoint}/{id}'.format(endpoint=self._endpoint, id=res_id)
        body = self._client.do_request(res_url, 'GET')

        return self._make_model(**body)

    def list(self, page_size=20, offset=0, limit=None, **filters):
        """
        Get a generator that iterates over all instances matching the specified filters

        Args:
            page_size (int): Page size to be used while scrolling
            offset (int): Initial scrolling offset
            limit (int): Record count after which to stop scrolling
            **filters: Filters to apply to the resource

        Returns:
            generator: Model generator

        """
        size = page_size

        formatted_filters = '&'.join(
            [str(k) + "=" + json.dumps(v) if type(v) == dict else str(k) + '=' + str(v) for k, v in filters.items()]
        )

        url_template = '{endpoint}?size={{size}}&offset={{offset}}&{filters}'.format(
            endpoint=self._endpoint,
            filters=formatted_filters
        )

        yield_count = 0

        while True:
            url = url_template.format(size=size, offset=offset)

            body = self._client.do_request(url, 'GET')

            for hit in body['hits']:
                yield_count += 1
                yield self._make_model(**hit)

                if limit is not None and yield_count >= limit:
                    break

            offset += size

            if offset >= body['total']:
                break

    def create(self, res):
        """
        Create a resource instance

        Args:
            res (Model): Resource instance

        Returns:
            Model: Created model (with generated ID, if applicable)

        """
        body = self._client.do_request(self._endpoint, 'POST', body=res.serialized)

        return self._make_model(**body)

    def update(self, res):
        """
        Update a resource instance

        Args:
            res (Model): Resource instance

        Returns:
            Model: Updated model

        """
        res_url = '{endpoint}/{id}'.format(endpoint=self._endpoint, id=res.id)
        body = self._client.do_request(res_url, 'PUT', body=res.serialized)

        return self._make_model(**body)

    def delete(self, res_id):
        """
        Delete a resource instance by ID

        Args:
            res_id: ID of the resource to delete
        """
        res_url = '{endpoint}/{id}'.format(endpoint=self._endpoint, id=res_id)
        self._client.do_request(res_url, 'DELETE')
