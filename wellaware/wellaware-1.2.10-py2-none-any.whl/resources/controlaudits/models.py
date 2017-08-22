from __future__ import unicode_literals

from wellaware.base import BaseEntity, JsonProperty


class ControlRequestType(object):
    ON_DEMAND_READ = 'ondemandread'
    SET_POINT_CHANGE = 'setpointchange'


class SetPointQuality(object):
    GOOD = 'good'
    UNCERTAIN = 'uncertain'
    BAD = 'bad'


class SetPointStatus(object):
    PENDING = 'pending'
    SUCCESS = 'success'
    FAILED = 'failed'


class ControlAudit(BaseEntity):
    """
    Control Audit Record.
    """

    status = JsonProperty('status')
    quality = JsonProperty('quality')
    pre_set_read_value = JsonProperty('preSetReadValue')
    value = JsonProperty('value')
    post_set_read_value = JsonProperty('postSetReadValue')
    read_timestamp = JsonProperty('readTimestamp')
    subject_id = JsonProperty('subjectId')
    subject_username = JsonProperty('subjectUsername')
    audit_created_timestamp = JsonProperty('auditCreatedTimestamp')
    audit_updated_timestamp = JsonProperty('auditUpdatedTimestamp')
    request_type = JsonProperty('requestType')

    @property
    def quality_is_good(self):
        return self.quality == SetPointQuality.GOOD

    @property
    def quality_is_uncertain(self):
        return self.quality == SetPointQuality.UNCERTAIN

    @property
    def quality_is_bad(self):
        return self.quality == SetPointQuality.BAD

    @property
    def status_is_failed(self):
        return self.status == SetPointStatus.FAILED

    @property
    def status_is_success(self):
        return self.status == SetPointStatus.SUCCESS

    @property
    def status_is_pending(self):
        return self.status == SetPointStatus.PENDING

    @property
    def is_on_demand_read(self):
        return self.request_type == ControlRequestType.ON_DEMAND_READ

    @property
    def is_on_demand_set(self):
        return  self.request_type == ControlRequestType.SET_POINT_CHANGE


__all__ = ['ControlAudit', 'ControlRequestType', 'SetPointQuality', 'SetPointStatus']