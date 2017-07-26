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

def meta_pagination(url, total, page):
    """Return pagination metadata"""
    next_page = '%s?page=%d' % (url, page+1)
    previous_page = '%s?page=%d' % (url, page-1)
    if total == page:
        next_page = None
    if page <= 1:
        previous_page = None

    return {
    'pagination': {
        'current_page': page, 'count': 1, 'total': total,
        'per_page': 1, 'total_pages': total, 'links': {
            'next_page': next_page,
            'previous_page': previous_page
        }}}

COMPONENTS = [
    {'description': 'Component A', 'enabled': True,
     'status': '2', 'id': 1, 'link': '',
     'created_at': '2017-01-26 18:15:06', 'group_id': 10, 'order': 0,
     'updated_at': '2017-04-20 09:21:06', 'status_name': 'Performance Issues',
     'deleted_at': None, 'name': 'Component A',
     'tags': {'test': 'value1'}},
    {'description': 'Component B', 'enabled': True,
     'status': '1', 'id': 2, 'link': '',
     'created_at': '2017-01-26 18:10:28', 'group_id': 10, 'order': 3,
     'updated_at': '2017-03-08 15:46:02', 'status_name': 'Operational',
     'deleted_at': None, 'name': 'Component B',
     'tags': {'test': 'value2'}},
    {'description': 'Component C', 'enabled': True,
     'status': '1', 'id': 3, 'link': '',
     'created_at': '2017-01-26 18:14:04', 'group_id': 10, 'order': 4,
     'updated_at': '2017-01-30 15:33:24', 'status_name': 'Operational',
     'deleted_at': None, 'name': 'Component C',
     'tags': {'test': 'value3'}},
    {'description': 'Component D', 'enabled': True,
     'status': '1', 'id': 4, 'link': '',
     'created_at': '2017-01-26 18:15:47', 'group_id': 10, 'order': 6,
     'updated_at': '2017-01-30 15:33:24', 'status_name': 'Operational',
     'deleted_at': None, 'name': 'Component D',
     'tags': {'test': 'value4'}},
    {'description': 'Component E', 'enabled': True,
     'status': '1', 'id': 5, 'link': '',
     'created_at': '2017-01-26 18:16:14', 'group_id': 10, 'order': 7,
     'updated_at': '2017-01-30 15:33:24', 'status_name': 'Operational',
     'deleted_at': None, 'name': 'Component E',
     'tags': {'test': 'value5'}},
    {'description': 'Component F', 'enabled': True,
     'status': '1', 'id': 6, 'link': '',
     'created_at': '2017-01-26 18:16:34', 'group_id': 10, 'order': 8,
     'updated_at': '2017-01-30 15:33:24', 'status_name': 'Operational',
     'deleted_at': None, 'name': 'Component F',
     'tags': {'test': 'value6'}}
]

COMPONENTS_BY_GROUP = {
    1: COMPONENTS[0:2],
    2: COMPONENTS[2:2],
    3: COMPONENTS[4:2]
}

COMPONENT_GROUPS = [
    {'updated_at': '2017-01-26 18:07:08', 'id': 1,
     'enabled_components': COMPONENTS_BY_GROUP[1],
     'lowest_human_status': 'Performance Issues',
     'created_at': '2017-01-26 18:06:23', 'name': 'Group A', 'order': 1},
    {'updated_at': '2017-01-27 12:17:08', 'id': 2,
     'enabled_components': COMPONENTS_BY_GROUP[2],
     'lowest_human_status': 'Operational',
     'created_at': '2017-01-27 12:17:23', 'name': 'Group B', 'order': 2},
    {'updated_at': '2017-01-28 16:08:18', 'id': 3,
     'enabled_components': COMPONENTS_BY_GROUP[3],
     'lowest_human_status': 'Operational',
     'created_at': '2017-01-28 16:08:18', 'name': 'Group C', 'order': 3}
]

INCIDENTS = [
    {'updated_at': '2017-07-21 18:48:28', 'scheduled_at': '2017-07-25 18:34:39',
     'visible': 1, 'name': 'Incident 1', 'id': 1,
     'human_status': 'Investigating',
     'deleted_at': None, 'status': '1', 'component_id': '1',
     'created_at': '2017-07-21 18:48:28',
     'message': 'Test incident 1.'},
    {'updated_at': '2017-07-21 18:49:22', 'scheduled_at': '2017-07-25 18:34:39',
     'visible': 1, 'name': 'Incident 2', 'id': 2,
     'human_status': 'Identified',
     'deleted_at': None, 'status': '2', 'component_id': '2',
     'created_at': '2017-07-21 18:49:22',
     'message': 'Test incident 2.'},
    {'updated_at': '2017-07-21 18:50:25', 'scheduled_at': '2017-07-25 18:34:39',
     'visible': 1, 'name': 'Incident 3', 'id': 3,
     'human_status': 'Investigating',
     'deleted_at': None, 'status': '1', 'component_id': '2',
     'created_at': '2017-07-21 18:50:25',
     'message': 'Test incident 3.'},
    {'updated_at': '2017-07-21 19:05:40', 'scheduled_at': '2017-07-25 18:34:39',
     'visible': 1, 'name': 'Incident 4', 'id': 4,
     'human_status': 'Investigating',
     'deleted_at': None, 'status': '1', 'component_id': '3',
     'created_at': '2017-07-21 19:05:40',
     'message': 'Test incident 4.'},
    {'updated_at': '2017-07-21 19:07:51', 'scheduled_at': '2017-07-25 18:34:39',
     'visible': 1, 'name': 'Incident 5', 'id': 5,
     'human_status': 'Watching',
     'deleted_at': None, 'status': '3', 'component_id': '4',
     'created_at': '2017-07-21 19:07:51',
     'message': 'Test incident 5.'},
    {'updated_at': '2017-07-21 19:08:51', 'scheduled_at': '2017-07-25 18:34:39',
     'visible': 1, 'name': 'Incident 6', 'id': 6,
     'human_status': 'Fixed',
     'deleted_at': None, 'status': '4', 'component_id': '4',
     'created_at': '2017-07-21 19:08:51',
     'message': 'Test incident 6.'}
]

METRICS = [
    {'calc_type': 0, 'updated_at': '2017-07-26 11:30:59',
     'description': 'Test metric 1', 'display_chart': True, 'places': 2,
     'default_view_name': 'Last 12 Hours', 'default_value': 0, 'suffix': 'unit',
     'default_view': 1, 'name': 'Metric 1', 'order': 0, 'id': 1,
     'threshold': 5, 'created_at': '2017-07-26 11:30:59'},
    {'calc_type': 0, 'updated_at': '2017-07-26 11:40:59',
     'description': 'Test metric 2', 'display_chart': True, 'places': 2,
     'default_view_name': 'Last 12 Hours', 'default_value': 0, 'suffix': 'unit',
     'default_view': 1, 'name': 'Metric 2', 'order': 0, 'id': 2,
     'threshold': 5, 'created_at': '2017-07-26 11:40:59'}
]

POINTS = [
    {'created_at': '2017-07-26 12:30:12', 'id': 1, 'metric_id': 1,
     'updated_at': '2017-07-26 12:30:12', 'calculated_value': 3, 'value': 3,
     'counter': 1},
    {'created_at': '2017-07-26 12:30:13', 'id': 2, 'metric_id': 1,
     'updated_at': '2017-07-26 12:30:13', 'calculated_value': 4, 'value': 4,
     'counter': 1}
]

SUBSCRIBERS = [
    {'verified_at': 'Wednesday 26th July 2017 11:54:27',
     'updated_at': '2017-07-26 11:54:27', 'id': 1,
     'email': 'jacquie@merci.com', 'created_at': '2017-07-26 11:54:27',
     'verify_code': 'n6fgQEMEKJST6mfpukRMnIn7y3H5vAJSuZcUBMbmYW'},
    {'verified_at': 'Wednesday 26th July 2017 11:56:22',
     'updated_at': '2017-07-26 11:56:22', 'id': 2,
     'email': 'michel@merci.com', 'created_at': '2017-07-26 11:56:22',
     'verify_code': 'UeJiEAqxvvENZyaa8UmpvS4jkp3hxa8tZ6XXX5jAyA'}
]
