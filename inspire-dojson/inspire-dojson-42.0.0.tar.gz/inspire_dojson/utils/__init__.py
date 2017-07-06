# -*- coding: utf-8 -*-
#
# This file is part of INSPIRE.
# Copyright (C) 2014-2017 CERN.
#
# INSPIRE is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# INSPIRE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with INSPIRE. If not, see <http://www.gnu.org/licenses/>.
#
# In applying this license, CERN does not waive the privileges and immunities
# granted to it by virtue of its status as an Intergovernmental Organization
# or submit itself to any jurisdiction.

"""DoJSON related utilities."""

from __future__ import absolute_import, division, print_function

import re
import six

try:
    from flask import current_app
except ImportError:  # pragma: no cover
    current_app = None

from jsonschema import validate as jsonschema_validate

from inspire_schemas.utils import LocalRefResolver

from ..utils.dedupers import dedupe_list, dedupe_list_of_dicts
from ..utils.helpers import force_list
from ..utils.text import encode_for_xml


def normalize_rank(rank):
    """Normalize the rank in order to be schema-compliant
    """
    normalized_ranks = {
        'BA': 'UNDERGRADUATE',
        'BACHELOR': 'UNDERGRADUATE',
        'BS': 'UNDERGRADUATE',
        'BSC': 'UNDERGRADUATE',
        'JUNIOR': 'JUNIOR',
        'MAS': 'MASTER',
        'MASTER': 'MASTER',
        'MS': 'MASTER',
        'MSC': 'MASTER',
        'PD': 'POSTDOC',
        'PHD': 'PHD',
        'POSTDOC': 'POSTDOC',
        'SENIOR': 'SENIOR',
        'STAFF': 'STAFF',
        'STUDENT': 'PHD',
        'UG': 'UNDERGRADUATE',
        'UNDERGRADUATE': 'UNDERGRADUATE',
        'VISITING SCIENTIST': 'VISITOR',
        'VISITOR': 'VISITOR',
    }
    if not rank:
        return None
    rank = rank.upper().replace('.', '')
    return normalized_ranks.get(rank, 'OTHER')


def force_single_element(obj):
    """Force an object to a list and return the first element."""
    lst = force_list(obj)
    if lst:
        return lst[0]
    return None


def get_recid_from_ref(ref_obj):
    """Retrieve recid from jsonref reference object.

    If no recid can be parsed, return None.
    """
    if not isinstance(ref_obj, dict):
        return None
    url = ref_obj.get('$ref', '')
    try:
        res = int(url.split('/')[-1])
    except ValueError:
        res = None
    return res


def get_record_ref(recid, endpoint='record'):
    """Create record jsonref reference object from recid.

    None recids will return a None object.
    Valid recids will return an object in the form of: {'$ref': url_for_record}
    """
    if recid is None:
        return None
    default_server = 'http://inspirehep.net'
    if current_app:
        server = current_app.config.get('SERVER_NAME') or default_server
    else:
        server = default_server
    # This config might also be http://inspirehep.net or
    # https://inspirehep.net.
    if not re.match('^https?://', server):
        server = 'http://{}'.format(server)
    return {'$ref': '{}/api/{}/{}'.format(server, endpoint, recid)}


def legacy_export_as_marc(json, tabsize=4):
    """Create the MARCXML representation using the producer rules."""

    def encode_for_marcxml(value):
        if isinstance(value, unicode):
            value = value.encode('utf8')
        return encode_for_xml(str(value), wash=True)

    export = ['<record>\n']

    for key, value in sorted(six.iteritems(json)):
        if not value:
            continue
        if key.startswith('00') and len(key) == 3:
            # Controlfield
            if isinstance(value, (tuple, list)):
                value = value[0]
            export += ['\t<controlfield tag="%s">%s'
                       '</controlfield>\n'.expandtabs(tabsize)
                       % (key, encode_for_marcxml(value))]
        else:
            tag = key[:3]
            try:
                ind1 = key[3].replace("_", "")
            except:
                ind1 = ""
            try:
                ind2 = key[4].replace("_", "")
            except:
                ind2 = ""
            if isinstance(value, dict):
                value = [value]
            for field in value:
                export += ['\t<datafield tag="%s" ind1="%s" '
                           'ind2="%s">\n'.expandtabs(tabsize)
                           % (tag, ind1, ind2)]
                if field:
                    for code, subfieldvalue in six.iteritems(field):
                        if subfieldvalue:
                            if isinstance(subfieldvalue, (list, tuple)):
                                for val in subfieldvalue:
                                    export += ['\t\t<subfield code="%s">%s'
                                               '</subfield>\n'.expandtabs(tabsize)
                                               % (code, encode_for_marcxml(val))]
                            else:
                                export += ['\t\t<subfield code="%s">%s'
                                           '</subfield>\n'.expandtabs(tabsize)
                                           % (code,
                                              encode_for_marcxml(subfieldvalue))]
                export += ['\t</datafield>\n'.expandtabs(tabsize)]
    export += ['</record>\n']
    return "".join(export)


def strip_empty_values(obj):
    """Recursively strips empty values."""
    if isinstance(obj, dict):
        for key, val in obj.items():
            new_val = strip_empty_values(val)
            # There are already lots of leaks in the callers of this function,
            # there's no need to make it idempotent and double memory.
            if new_val is not None:
                obj[key] = new_val
            else:
                del obj[key]
        return obj or None
    elif isinstance(obj, (list, tuple, set)):
        new_obj = []
        for val in obj:
            new_val = strip_empty_values(val)
            if new_val is not None:
                new_obj.append(new_val)
        return type(obj)(new_obj) or None
    elif obj or obj is False or obj == 0:
        return obj
    else:
        return None


def dedupe_all_lists(obj):
    """Recursively remove duplucates from all lists."""
    squared_dedupe_len = 10
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = dedupe_all_lists(value)
        return obj
    elif isinstance(obj, (list, tuple, set)):
        new_elements = [dedupe_all_lists(v) for v in obj]
        if len(new_elements) < squared_dedupe_len:
            new_obj = dedupe_list(new_elements)
        else:
            new_obj = dedupe_list_of_dicts(new_elements)
        return type(obj)(new_obj)
    else:
        return obj


def validate(instance, schema):
    return jsonschema_validate(
        instance, schema, resolver=LocalRefResolver('', {}))
