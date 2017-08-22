from __future__ import unicode_literals

from wellaware._compat import array_types, long_
from wellaware.base import BaseResource
from wellaware.constants import make_headers
from wellaware.resources.sitegroups.models import SiteGroup, SiteGroupSummary, SiteGroupViewConfig, SiteGroupNotificationSetting, SiteGroupNotificationResponse
from wellaware.resources.sites.models import Site
from wellaware.resources.subjects.models import Subject


class SiteGroups(BaseResource):

    @classmethod
    def endpoint(cls):
        return '/sitegroups'

    @classmethod
    def endpoint_single(cls):
        return '/sitegroups/{id}'

    @classmethod
    def endpoint_extra(cls, extra):
        return '/sitegroups/{id}' + extra

    @classmethod
    def entity_class(cls):
        return SiteGroup

    @classmethod
    def create(cls, token, sitegroup, parameters=None):
        cls.validate_is_entity(sitegroup, SiteGroup)
        return cls._create(token, sitegroup, parameters=parameters)

    @classmethod
    def retrieve_one(cls, token, sitegroup_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        return cls._retreive_one(token, sitegroup_id, parameters=parameters)

    @classmethod
    def retrieve_all(cls, token, parameters=None):
        return cls._retrieve_all(token, parameters=parameters)

    @classmethod
    def update(cls, token, sitegroup, parameters=None):
        cls.validate_is_entity(sitegroup, SiteGroup)
        return cls._update(token, sitegroup, parameters=parameters)

    @classmethod
    def delete(cls, token, sitegroup_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        return cls._delete(token, sitegroup_id, parameters=parameters)

    # Subject relationships
    @classmethod
    def assign_subject_to_sitegroup(cls, token, sitegroup_id, subject_id, notification_setting, parameters=None):
        if parameters is None:
            parameters = {}
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        subject_id = cls.get_entity_id(subject_id, Subject)
        cls.validate_is_entity(notification_setting, SiteGroupNotificationSetting)
        parameters['notifySms'] = notification_setting.notify_sms or False
        parameters['notifyEmail'] = notification_setting.notify_email or False
        ids = {'id': sitegroup_id, 'subject_id': subject_id}
        response = cls.REST_CLIENT.post(
            cls.get_base_uri(cls.endpoint_extra('/subjects/rel/{subject_id}'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        return response

    @classmethod
    def get_all_subject_ids_of_sitegroup(cls, token, sitegroup_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        ids = {'id': sitegroup_id}
        response = cls.REST_CLIENT.get(
            cls.get_base_uri(cls.endpoint_extra('/subjects/rel'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        return response.json()

    @classmethod
    def get_all_subject_notification_settings_of_sitegroup(cls, token, sitegroup_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        ids = {'id': sitegroup_id}
        response = cls.REST_CLIENT.get(
            cls.get_base_uri(cls.endpoint_extra('/subjects/rel/notifications'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        return SiteGroupNotificationResponse.from_dict(response.json())

    @classmethod
    def update_subject_notification_settings(cls, token, sitegroup_id, subject_id, notification_setting, parameters=None):
        if parameters is None:
            parameters = {}
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        subject_id = cls.get_entity_id(subject_id, Subject)
        cls.validate_is_entity(notification_setting, SiteGroupNotificationSetting)
        parameters['notifySms'] = notification_setting.notify_sms or False
        parameters['notifyEmail'] = notification_setting.notify_email or False
        ids = {'id': sitegroup_id, 'subject_id': subject_id}
        response = cls.REST_CLIENT.put(
            cls.get_base_uri(cls.endpoint_extra('/subjects/rel/{subject_id}'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        return response

    @classmethod
    def remove_subject_from_sitegroup(cls, token, sitegroup_id, subject_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        subject_id = cls.get_entity_id(subject_id, Subject)
        ids = {'id': sitegroup_id, 'subject_id': subject_id}
        response = cls.REST_CLIENT.delete(
            cls.get_base_uri(cls.endpoint_extra('/subjects/rel/{subject_id}'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        return response

    # Sites
    @classmethod
    def get_site_ids_in_sitegroup(cls, token, sitegroup_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        ids = {'id': sitegroup_id}
        response = cls.REST_CLIENT.get(
            cls.get_base_uri(cls.endpoint_extra('/sites/rel'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        return response.json()

    @classmethod
    def assign_site_to_sitegroup(cls, token, sitegroup_id, site_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        site_id = cls.get_entity_id(site_id, Site)
        ids = {'id': sitegroup_id, 'site_id': site_id}
        response = cls.REST_CLIENT.put(
            cls.get_base_uri(cls.endpoint_extra('/sites/rel/{site_id}'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        return response

    @classmethod
    def remove_site_from_sitegroup(cls, token, sitegroup_id, site_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        site_id = cls.get_entity_id(site_id, Site)
        ids = {'id': sitegroup_id, 'site_id': site_id}
        response = cls.REST_CLIENT.delete(
            cls.get_base_uri(cls.endpoint_extra('/sites/rel/{site_id}'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        return response

    # Summary Config
    @classmethod
    def get_sitegroup_view_config(cls, token, sitegroup_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        ids = {'id': sitegroup_id}
        response = cls.REST_CLIENT.get(
            cls.get_base_uri(cls.endpoint_extra('/meta/viewconfig'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        summaries = response.json().get('summaries', [])
        if isinstance(summaries, array_types):
            results = []
            for r in summaries:
                if isinstance(r, dict):
                    results.append(SiteGroupSummary.from_dict(r))
        else:
            results = [SiteGroupSummary.from_dict(response.json())]
        return SiteGroupViewConfig(summaries=results)

    @classmethod
    def update_sitegroup_view_config(cls, token, sitegroup_id, view_config, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        cls.validate_is_entity(view_config, SiteGroupViewConfig)
        for summary in view_config.summaries:
            cls.validate_is_entity(summary, SiteGroupSummary)
        ids = {'id': sitegroup_id}
        response = cls.REST_CLIENT.put(
            cls.get_base_uri(cls.endpoint_extra('/meta/viewconfig'), **ids),
            json=view_config.get_json_data(),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        summaries = response.json().get('summaries', [])
        if isinstance(summaries, array_types):
            results = []
            for r in summaries:
                if isinstance(r, dict):
                    results.append(SiteGroupSummary.from_dict(r))
        else:
            results = [SiteGroupSummary.from_dict(response.json())]
        return SiteGroupViewConfig(summaries=results)

    @classmethod
    def delete_sitegroup_view_config(cls, token, sitegroup_id, parameters=None):
        sitegroup_id = cls.get_entity_id(sitegroup_id, SiteGroup)
        ids = {'id': sitegroup_id}
        response = cls.REST_CLIENT.delete(
            cls.get_base_uri(cls.endpoint_extra('/meta/viewconfig'), **ids),
            headers=make_headers(token),
            params=parameters
        )
        response = cls.REST_CLIENT.handle_response(response)
        return response


__all__ = ['SiteGroup', 'SiteGroups', 'SiteGroupNotificationSetting', 'SiteGroupViewConfig',
           'SiteGroupNotificationResponse', 'SiteGroupSummary']
