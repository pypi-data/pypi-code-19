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
Views for tempmon probes
"""

from __future__ import unicode_literals, absolute_import

from rattail_tempmon.db import model as tempmon

import formalchemy as fa

from tailbone import forms
from tailbone.db import TempmonSession
from tailbone.views.tempmon import MasterView, ClientFieldRenderer


def unique_config_key(value, field):
    probe = field.parent.model
    query = TempmonSession.query(tempmon.Probe)\
                   .filter(tempmon.Probe.config_key == value)
    if probe.uuid:
        query = query.filter(tempmon.Probe.uuid != probe.uuid)
    if query.count():
        raise fa.ValidationError("Config key must be unique")


class TempmonProbeView(MasterView):
    """
    Master view for tempmon probes.
    """
    model_class = tempmon.Probe
    model_title = "TempMon Probe"
    model_title_plural = "TempMon Probes"
    route_prefix = 'tempmon.probes'
    url_prefix = '/tempmon/probes'

    def _preconfigure_grid(self, g):
        g.joiners['client'] = lambda q: q.join(tempmon.Client)
        g.sorters['client'] = g.make_sorter(tempmon.Client.config_key)
        g.default_sortkey = 'client'
        g.config_key.set(label="Key")
        g.appliance_type.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.TEMPMON_APPLIANCE_TYPE))
        g.status.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.TEMPMON_PROBE_STATUS))

    def configure_grid(self, g):
        g.configure(
            include=[
                g.client,
                g.config_key,
                g.appliance_type,
                g.description,
                g.device_path,
                g.enabled,
                g.status,
            ],
            readonly=True)

    def _preconfigure_fieldset(self, fs):
        fs.config_key.set(validate=unique_config_key)
        fs.client.set(label="TempMon Client", renderer=ClientFieldRenderer)
        fs.appliance_type.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.TEMPMON_APPLIANCE_TYPE))
        fs.status.set(renderer=forms.renderers.EnumFieldRenderer(self.enum.TEMPMON_PROBE_STATUS))

    def configure_fieldset(self, fs):
        fs.configure(
            include=[
                fs.client,
                fs.config_key,
                fs.appliance_type,
                fs.description,
                fs.device_path,
                fs.critical_temp_min,
                fs.good_temp_min,
                fs.good_temp_max,
                fs.critical_temp_max,
                fs.therm_status_timeout,
                fs.status_alert_timeout,
                fs.enabled,
                fs.status,
            ])
        if self.creating or self.editing:
            del fs.status


def includeme(config):
    TempmonProbeView.defaults(config)
