# -*- coding: utf-8 -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2016 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU Affero General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option)
#  any later version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for
#  more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Email config for tempmon-server
"""

from __future__ import unicode_literals, absolute_import

from rattail.db import model
from rattail.mail import Email
from rattail.time import localtime


class tempmon(object):
    """
    Generic base class for all tempmon-related emails; adds common sample data.
    """
    
    def sample_data(self, request):
        now = localtime(self.config)
        client = model.TempmonClient(config_key='testclient', hostname='testclient')
        probe = model.TempmonProbe(config_key='testprobe', description="Test Probe")
        client.probes.append(probe)
        return {
            'probe': probe,
            'status': self.enum.TEMPMON_PROBE_STATUS[self.enum.TEMPMON_PROBE_STATUS_ERROR],
            'reading': model.TempmonReading(),
            'taken': now,
            'now': now,
        }


class tempmon_critical_temp(tempmon, Email):
    """
    Sent when a tempmon probe takes a reading which is "critical" in either the
    high or low sense.
    """
    default_subject = "Critical temperature detected"
    
    def sample_data(self, request):
        data = super(tempmon_critical_temp, self).sample_data(request)
        data['status'] = self.enum.TEMPMON_PROBE_STATUS[self.enum.TEMPMON_PROBE_STATUS_CRITICAL_TEMP]
        return data


class tempmon_error(tempmon, Email):
    """
    Sent when a tempmon probe is noticed to have some error, i.e. no current readings.
    """
    default_subject = "Probe error detected"
    
    def sample_data(self, request):
        data = super(tempmon_error, self).sample_data(request)
        data['status'] = self.enum.TEMPMON_PROBE_STATUS[self.enum.TEMPMON_PROBE_STATUS_ERROR]
        data['taken'] = None
        return data


class tempmon_good_temp(tempmon, Email):
    """
    Sent whenever a tempmon probe first takes a "good temp" reading, after
    having previously had some bad reading(s).
    """
    default_subject = "Good temperature detected"
    
    def sample_data(self, request):
        data = super(tempmon_good_temp, self).sample_data(request)
        data['status'] = self.enum.TEMPMON_PROBE_STATUS[self.enum.TEMPMON_PROBE_STATUS_GOOD_TEMP]
        return data


class tempmon_high_temp(tempmon, Email):
    """
    Sent when a tempmon probe takes a reading which is above the "maximum good
    temp" range, but still below the "critically high temp" threshold.
    """
    default_subject = "High temperature detected"
    
    def sample_data(self, request):
        data = super(tempmon_high_temp, self).sample_data(request)
        data['status'] = self.enum.TEMPMON_PROBE_STATUS[self.enum.TEMPMON_PROBE_STATUS_HIGH_TEMP]
        return data


class tempmon_low_temp(tempmon, Email):
    """
    Sent when a tempmon probe takes a reading which is below the "minimum good
    temp" range, but still above the "critically low temp" threshold.
    """
    default_subject = "Low temperature detected"

    def sample_data(self, request):
        data = super(tempmon_low_temp, self).sample_data(request)
        data['status'] = self.enum.TEMPMON_PROBE_STATUS[self.enum.TEMPMON_PROBE_STATUS_LOW_TEMP]
        return data
