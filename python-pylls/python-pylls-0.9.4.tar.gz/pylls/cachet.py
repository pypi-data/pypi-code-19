#
#    Cachet API python client and interface (python-pylls)
#
#    Copyright (C) 2017 Denis Pompilio (jawa) <denis.pompilio@gmail.com>
#
#    This file is part of python-pylls
#
#    This program is free software; you can redistribute it and/or
#    modify it under the terms of the GNU General Public License
#    as published by the Free Software Foundation; either version 2
#    of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, see <http://www.gnu.org/licenses/>.

from pylls import client


class ApiParams(dict):
    """API parameters storage

    Convenience class for API parameters management.
    The :meth:`__setitem__` method is overridden to skip None value items.

    **Example:**

        >>> params = ApiParams(first=1, second=2)
        >>> params['none'] = None
        >>> params['third'] = 3
        >>> print(sorted(params.items()))
        [('first', 1), ('second', 2), ('third', 3)]
    """
    def __setitem__(self, key, value):
        if value is not None:
            super(ApiParams, self).__setitem__(key, value)


class Ping(client.CachetAPIEndPoint):
    """Ping API endpoint
    """
    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super(Ping, self).__init__(*args, **kwargs)

    def get(self):
        """Test that the API is responding to your requests

        :return: Ping response data (:class:`str`)

        .. seealso:: https://docs.cachethq.io/reference#ping
        """
        return self._get('ping')['data']


class Version(client.CachetAPIEndPoint):
    """Version API endpoint
    """
    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super(Version, self).__init__(*args, **kwargs)

    def get(self):
        """Get the Cachet version

        :return: Cachet version data (:class:`str`)

        .. seealso:: https://docs.cachethq.io/reference#version
        """
        return self._get('version')['data']


class Components(client.CachetAPIEndPoint):
    """Components API endpoint
    """
    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super(Components, self).__init__(*args, **kwargs)
        self._groups = None

    @property
    def groups(self):
        """Component groups

        Special property which point to a :class:`~pylls.cachet.ComponentGroups`
        instance for convenience. This instance is initialized on first call.
        """
        if not self._groups:
            self._groups = ComponentGroups(self.api_client)
        return self._groups

    def get(self, component_id=None, **kwargs):
        """Get components

        :param component_id: Component ID (optional)
        :return: Components data (:class:`Generator`)

        Additional named arguments may be passed and are directly transmitted
        to API. It is useful to use the API search features.

        .. seealso:: https://docs.cachethq.io/reference#get-components
        .. seealso:: https://docs.cachethq.io/docs/advanced-api-usage
        """
        path = 'components'
        if component_id is not None:
            path += '/%s' % component_id
        return self.paginate_get(path, data=kwargs)

    def create(self, name, status, description="", link="", order=0,
               group_id=0, enabled=True):
        """Create a new component

        :param str name: Name of the component
        :param int status: Status of the component; 1-4
        :param str description: Description of the component (optional)
        :param str link: A hyperlink to the component (optional)
        :param int order: Order of the component (optional)
        :param int group_id: The group ID of the component (optional)
        :param bool enabled: Whether the component is enabled (optional)
        :return: Created component data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#components
        .. seealso:: https://docs.cachethq.io/docs/component-statuses
        """
        data = ApiParams()
        data['name'] = name
        data['status'] = status
        data['description'] = description
        data['link'] = link
        data['order'] = order
        data['group_id'] = group_id
        data['enabled'] = enabled
        return self._post('components', data=data)['data']

    def update(self, component_id, name=None, status=None, description=None,
               link=None, order=None, group_id=None, enabled=True):
        """Update a component

        :param int component_id: Component ID
        :param str name: Name of the component (optional)
        :param int status: Status of the component; 1-4
        :param str description: Description of the component (optional)
        :param str link: A hyperlink to the component (optional)
        :param int order: Order of the component (optional)
        :param int group_id: The group ID of the component (optional)
        :param bool enabled: Whether the component is enabled (optional)
        :return: Updated component data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#components
        .. seealso:: https://docs.cachethq.io/docs/component-statuses
        """
        data = ApiParams()
        data['component'] = component_id
        data['name'] = name
        data['status'] = status
        data['description'] = description
        data['link'] = link
        data['order'] = order
        data['group_id'] = group_id
        data['enabled'] = enabled
        return self._put('components/%s' % component_id, data=data)['data']

    def delete(self, component_id):
        """Delete a component

        :param int component_id: Component ID
        :return: :obj:`None`

        .. seealso:: https://docs.cachethq.io/reference#delete-a-components
        """
        self._delete('components/%s' % component_id)


class ComponentGroups(client.CachetAPIEndPoint):
    """Component groups API endpoint
    """
    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super(ComponentGroups, self).__init__(*args, **kwargs)

    def get(self, group_id=None, **kwargs):
        """Get component groups

        :param group_id: Component group ID (optional)
        :return: Component groups data (:class:`dict`)

        Additional named arguments may be passed and are directly transmitted
        to API. It is useful to use the API search features.

        .. seealso:: https://docs.cachethq.io/reference#get-componentgroups
        .. seealso:: https://docs.cachethq.io/docs/advanced-api-usage
        """
        path = 'components/groups'
        if group_id is not None:
            path += '/%s' % group_id
        return self.paginate_get(path, data=kwargs)

    def create(self, name, order=None, collapsed=None):
        """Create a new Component Group

        :param str name: Name of the component group
        :param int order: Order of the component group
        :param int collapsed: Collapse the group? 0-2
        :return: Created component group data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#post-componentgroups
        """
        data = ApiParams()
        data['name'] = name
        data['order'] = order
        data['collapsed'] = collapsed
        return self._post('components/groups', data=data)['data']

    def update(self, group_id, name=None, order=None, collapsed=None):
        """Update a Component Group

        :param int group_id: Component Group ID
        :param str name: Name of the component group
        :param int order: Order of the group
        :param int collapsed: Collapse the group?
        :return: Updated component group data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#put-component-group
        """
        data = ApiParams()
        data['group'] = group_id
        data['name'] = name
        data['order'] = order
        data['collapsed'] = collapsed
        return self._put('components/groups/%s' % group_id, data=data)['data']

    def delete(self, group_id):
        """Delete a Component Group

        :param int group_id: Component Group ID
        :return: :obj:`None`

        .. seealso:: https://docs.cachethq.io/reference#delete-a-component
        """
        self._delete('components/groups/%s' % group_id)


class Incidents(client.CachetAPIEndPoint):
    """Incidents API endpoint
    """
    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super(Incidents, self).__init__(*args, **kwargs)

    def get(self, incident_id=None, **kwargs):
        """Get incidents

        :param int incident_id:
        :return: Incidents data (:class:`dict`)

        Additional named arguments may be passed and are directly transmitted
        to API. It is useful to use the API search features.

        .. seealso:: https://docs.cachethq.io/reference#get-incidents
        .. seealso:: https://docs.cachethq.io/docs/advanced-api-usage
        """
        path = 'incidents'
        if incident_id is not None:
            path += '/%s' % incident_id
        return self.paginate_get(path, data=kwargs)

    def create(self, name, message, status, visible, component_id=None,
               component_status=None, notify=None, created_at=None,
               template=None, tplvars=None):
        """Create a new Incident

        :param str name: Name of the incident
        :param str message: Incident explanation message
        :param int status: Status of the incident
        :param int visible: Whether the incident is publicly visible
        :param int component_id: Component to update
        :param int component_status: The status to update the given component
        :param bool notify: Whether to notify subscribers
        :param str created_at: When the incident was created
        :param str template: The template slug to use
        :param list tplvars: The variables to pass to the template
        :return: Created incident data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#incidents
        """
        data = ApiParams()
        data['name'] = name
        data['message'] = message
        data['status'] = status
        data['visible'] = visible
        data['component_id'] = component_id
        data['component_status'] = component_status
        data['notify'] = notify
        data['created_at'] = created_at
        data['template'] = template
        data['vars'] = tplvars
        return self._post('incidents', data=data)['data']

    def update(self, incident_id, name=None, message=None, status=None,
               visible=None, component_id=None, component_status=None,
               notify=None, created_at=None, template=None, tpl_vars=None):
        """Update an Incident

        :param int incident_id: Incident ID
        :param str name: Name of the incident
        :param str message: Incident explanation message
        :param int status: Status of the incident
        :param int visible: Whether the incident is publicly visible
        :param int component_id: Component to update
        :param int component_status: The status to update the given component
        :param bool notify: Whether to notify subscribers
        :param str created_at: When the incident was created
        :param str template: The template slug to use
        :param list tpl_vars: The variables to pass to the template
        :return: Created incident data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#update-an-incident
        """
        data = ApiParams()
        data['name'] = name
        data['message'] = message
        data['status'] = status
        data['visible'] = visible
        data['component_id'] = component_id
        data['component_status'] = component_status
        data['notify'] = notify
        data['created_at'] = created_at
        data['template'] = template
        data['vars'] = tpl_vars
        return self._put('incidents/%s' % incident_id, data=data)['data']

    def delete(self, incident_id):
        """Delete an Incident

        :param int incident_id: Incident ID
        :return: :obj:`None`

        .. seealso:: https://docs.cachethq.io/reference#delete-an-incident
        """
        self._delete('incidents/%s' % incident_id)


class Metrics(client.CachetAPIEndPoint):
    """Metrics API endpoint
    """
    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super(Metrics, self).__init__(*args, **kwargs)
        self._points = None

    @property
    def points(self):
        """Metric points

        Special property which point to a :class:`~pylls.cachet.MetricPoints`
        instance for convenience. This instance is initialized on first call.
        """
        if not self._points:
            self._points = MetricPoints(self.api_client)
        return self._points

    def get(self, metric_id=None, **kwargs):
        """Get metrics

        :param int metric_id: Metric ID
        :return: Metrics data (:class:`dict`)

        Additional named arguments may be passed and are directly transmitted
        to API. It is useful to use the API search features.

        .. seealso:: https://docs.cachethq.io/reference#get-metrics
        .. seealso:: https://docs.cachethq.io/docs/advanced-api-usage
        """
        path = 'metrics'
        if metric_id is not None:
            path += '/%s' % metric_id
        return self.paginate_get(path, data=kwargs)

    def create(self, name, suffix, description, default_value, display=None):
        """Create a new Metric

        :param str name: Name of metric
        :param str suffix: Metric unit
        :param str description: Description of what the metric is measuring
        :param int default_value: Default value to use when a point is added
        :param int display: Display the chart on the status page
        :return: Created metric data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#metrics
        """
        data = ApiParams()
        data['name'] = name
        data['suffix'] = suffix
        data['description'] = description
        data['default_value'] = default_value
        data['display'] = display
        return self._post('metrics', data=data)['data']

    def delete(self, metric_id):
        """Delete a Metric

        :param int metric_id: Metric ID
        :return: :obj:`None`

        .. seealso:: https://docs.cachethq.io/reference#delete-a-metric
        """
        self._delete('metrics/%s' % metric_id)


class MetricPoints(client.CachetAPIEndPoint):
    """MetricPoints API endpoint
    """
    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super(MetricPoints, self).__init__(*args, **kwargs)

    def get(self, metric_id, **kwargs):
        """Get Points for a Metric

        :param int metric_id: Metric ID
        :return: Metric points data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#get-metric-points
        """
        return self.paginate_get('metrics/%s/points' % metric_id, **kwargs)

    def create(self, metric_id, value, timestamp=None):
        """Add a Metric Point to a Metric

        :param int metric_id: Metric ID
        :param int value: Value to plot on the metric graph
        :param str timestamp: Unix timestamp of the point was measured
        :return: Created metric point data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#post-metric-points
        """
        data = ApiParams()
        data['value'] = value
        data['timestamp'] = timestamp
        return self._post('metrics/%s/points' % metric_id, data=data)['data']

    def delete(self, metric_id, point_id):
        """Delete a Metric Point

        :param metric_id: Metric ID
        :param point_id: Metric point ID
        :return: :obj:`None`

        .. seealso:: https://docs.cachethq.io/reference#delete-a-metric-point
        """
        self._delete('metrics/%s/points/%s' % (metric_id, point_id))


class Subscribers(client.CachetAPIEndPoint):
    """Subscribers API endpoint
    """
    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super(Subscribers, self).__init__(*args, **kwargs)

    def get(self, **kwargs):
        """Returns all subscribers

        :return: Subscribers data (:class:`dict`)

        Additional named arguments may be passed and are directly transmitted
        to API. It is useful to use the API search features.

        .. seealso:: https://docs.cachethq.io/reference#get-subscribers
        .. seealso:: https://docs.cachethq.io/docs/advanced-api-usage
        """

        return self.paginate_get('subscribers', data=kwargs)

    def create(self, email, verify=None, components=None):
        """Create a new subscriber

        :param str email: Email address to subscribe
        :param bool verify: Whether to send verification email
        :param list components: Components ID list, defaults to all
        :return: Created subscriber data (:class:`dict`)

        .. seealso:: https://docs.cachethq.io/reference#subscribers
        """
        data = ApiParams()
        data['email'] = email
        data['verify'] = verify
        data['components'] = components
        return self._post('subscribers', data=data)['data']

    def delete(self, subscriber_id):
        """Delete a Subscriber

        :param int subscriber_id: Subscriber ID
        :return: :obj:`None`

        .. seealso:: https://docs.cachethq.io/reference#delete-subscriber
        """
        self._delete('subscribers/%s' % subscriber_id)


class Actions(client.CachetAPIEndPoint):
    """Actions API endpoint

    This endpoint is not implemented in Cachet 2.3 and will be released in 2.4

    .. seealso:: https://docs.cachethq.io/reference#get-actions
    """
    def __init__(self, *args, **kwargs):
        """Initialization method"""
        super(Actions, self).__init__(*args, **kwargs)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
