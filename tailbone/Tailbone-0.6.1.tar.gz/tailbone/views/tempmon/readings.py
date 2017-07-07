# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2017 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Views for tempmon readings
"""

from __future__ import unicode_literals, absolute_import

from sqlalchemy import orm

from rattail_tempmon.db import model as tempmon

import formalchemy as fa

from tailbone.views.tempmon import MasterView, ClientFieldRenderer, ProbeFieldRenderer


class TempmonReadingView(MasterView):
    """
    Master view for tempmon readings.
    """
    model_class = tempmon.Reading
    model_title = "TempMon Reading"
    model_title_plural = "TempMon Readings"
    route_prefix = 'tempmon.readings'
    url_prefix = '/tempmon/readings'
    creatable = False
    editable = False

    def query(self, session):
        return session.query(tempmon.Reading)\
                      .join(tempmon.Client)\
                      .options(orm.joinedload(tempmon.Reading.client))

    def _preconfigure_grid(self, g):

        g.append(fa.Field('client_key', value=lambda r: r.client.config_key))
        g.sorters['client_key'] = g.make_sorter(tempmon.Client.config_key)
        g.filters['client_key'] = g.make_filter('client_key', tempmon.Client.config_key)

        g.append(fa.Field('client_host', value=lambda r: r.client.hostname))
        g.sorters['client_host'] = g.make_sorter(tempmon.Client.hostname)
        g.filters['client_host'] = g.make_filter('client_host', tempmon.Client.hostname)

        g.joiners['probe'] = lambda q: q.join(tempmon.Probe,
                                              tempmon.Probe.uuid == tempmon.Reading.probe_uuid)
        g.sorters['probe'] = g.make_sorter(tempmon.Probe.description)
        g.filters['probe'] = g.make_filter('probe', tempmon.Probe.description)

        g.default_sortkey = 'taken'
        g.default_sortdir = 'desc'

    def configure_grid(self, g):
        g.configure(
            include=[
                g.client_key,
                g.client_host,
                g.probe,
                g.taken,
                g.degrees_f,
            ],
            readonly=True)

    def _preconfigure_fieldset(self, fs):
        fs.client.set(label="TempMon Client", renderer=ClientFieldRenderer)
        fs.probe.set(label="TempMon Probe", renderer=ProbeFieldRenderer)

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.client,
                fs.probe,
                fs.taken,
                fs.degrees_f,
            ])


def includeme(config):
    TempmonReadingView.defaults(config)
