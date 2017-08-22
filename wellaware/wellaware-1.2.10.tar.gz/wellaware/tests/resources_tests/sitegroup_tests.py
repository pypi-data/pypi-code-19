from __future__ import unicode_literals

from wellaware.client import SiteGroup, SiteGroups, Site, SiteGroupViewConfig, SiteGroupSummary, \
    SiteGroupNotificationSetting, SiteGroupNotificationResponse, Subject, Token
from wellaware.tests.base import *


class SiteGroupTests(BaseClientTestCase):

    token = Token(WA_ADMIN_TOKEN)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_create_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup')
        resp = {'name': 'Test SiteGroup', 'id': 10}
        responses.add(responses.POST, 'http://localhost/sitegroups', json=resp, status=200)

        e = SiteGroups.create(self.token, sitegroup=sitegroup)
        self.assertIsInstance(e, SiteGroup)
        self.assertEquals(sitegroup.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_retrieve_one_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        resp = {'name': 'Test SiteGroup', 'id': 10}
        responses.add(responses.GET, 'http://localhost/sitegroups/10', json=resp, status=200)

        e = SiteGroups.retrieve_one(self.token, sitegroup_id=sitegroup.id)
        self.assertIsInstance(e, SiteGroup)
        self.assertEquals(sitegroup.name, e.name)
        self.assertEquals(10, e.id)

        e = SiteGroups.retrieve_one(self.token, sitegroup_id=sitegroup)
        self.assertIsInstance(e, SiteGroup)
        self.assertEquals(sitegroup.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_retrieve_all_sitegroups(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        resp = [{'name': 'Test SiteGroup', 'id': 10}]
        responses.add(responses.GET, 'http://localhost/sitegroups', json=resp, status=200)

        el = SiteGroups.retrieve_all(self.token)
        self.assertIsInstance(el, list)
        e = el[0]
        self.assertEquals(sitegroup.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_update_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        resp = {'name': 'Test SiteGroup', 'id': 10}
        responses.add(responses.PUT, 'http://localhost/sitegroups/10', json=resp, status=200)

        e = SiteGroups.update(self.token, sitegroup=sitegroup)
        self.assertIsInstance(e, SiteGroup)
        self.assertEquals(sitegroup.name, e.name)
        self.assertEquals(10, e.id)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_delete_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        resp = {'name': 'Test SiteGroup', 'id': 10}
        responses.add(responses.DELETE, 'http://localhost/sitegroups/10', body='', status=204)

        r = SiteGroups.delete(self.token, sitegroup_id=sitegroup)
        self.assertEquals(204, r.status_code)

        r = SiteGroups.delete(self.token, sitegroup_id=sitegroup.id)
        self.assertEquals(204, r.status_code)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_assign_subject_to_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        subject = Subject(username='test', id=100)
        resp = {'name': 'Test SiteGroup', 'id': 10}
        responses.add(
            responses.POST, 'http://localhost/sitegroups/10/subjects/rel/100?notifyEmail=True&notifySms=False', body='',
            status=204, match_querystring=True
        )
        notification_setting = SiteGroupNotificationSetting(notify_email=True)

        r = SiteGroups.assign_subject_to_sitegroup(self.token, sitegroup_id=sitegroup, subject_id=subject,
                                                   notification_setting=notification_setting)
        self.assertEquals(204, r.status_code)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_get_all_subject_ids_of_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        resp = [100, ]
        responses.add(
            responses.GET, 'http://localhost/sitegroups/10/subjects/rel',
            json=resp, status=204, match_querystring=True
        )

        r = SiteGroups.get_all_subject_ids_of_sitegroup(self.token, sitegroup_id=sitegroup)
        self.assertListEqual([100, ], r)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_get_all_subject_notification_settings_of_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        resp = {'settings': {'100': {'notifyEmail': False, 'notifySms': True}}}
        responses.add(
            responses.GET, 'http://localhost/sitegroups/10/subjects/rel/notifications',
            json=resp, status=204, match_querystring=True
        )

        r = SiteGroups.get_all_subject_notification_settings_of_sitegroup(self.token, sitegroup_id=sitegroup)
        self.assertIsInstance(r, SiteGroupNotificationResponse)
        nsm = r.settings
        self.assertIsInstance(nsm, dict)
        ns = nsm[100]
        self.assertIsInstance(ns, SiteGroupNotificationSetting)
        self.assertTrue(ns.notify_sms)
        self.assertFalse(ns.notify_email)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_update_subject_notification_settings(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        subject = Subject(username='test', id=100)
        responses.add(
            responses.PUT, 'http://localhost/sitegroups/10/subjects/rel/100?notifyEmail=True&notifySms=False', body='',
            status=204, match_querystring=True
        )
        notification_setting = SiteGroupNotificationSetting(notify_email=True)

        r = SiteGroups.update_subject_notification_settings(self.token, sitegroup_id=sitegroup, subject_id=subject,
                                                            notification_setting=notification_setting)
        self.assertEquals(204, r.status_code)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_remove_subject_from_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        subject = Subject(username='test', id=100)
        responses.add(
            responses.DELETE, 'http://localhost/sitegroups/10/subjects/rel/100', body='',
            status=204, match_querystring=True
        )

        r = SiteGroups.remove_subject_from_sitegroup(self.token, sitegroup_id=sitegroup, subject_id=subject)
        self.assertEquals(204, r.status_code)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_get_site_ids_in_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        resp = [100, ]
        responses.add(
            responses.GET, 'http://localhost/sitegroups/10/sites/rel',
            json=resp, status=204, match_querystring=True
        )

        r = SiteGroups.get_site_ids_in_sitegroup(self.token, sitegroup_id=sitegroup)
        self.assertListEqual([100, ], r)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_assign_site_to_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        site = Site(username='test', id=100)
        responses.add(
            responses.PUT, 'http://localhost/sitegroups/10/sites/rel/100', body='',
            status=204, match_querystring=True
        )

        r = SiteGroups.assign_site_to_sitegroup(self.token, sitegroup_id=sitegroup, site_id=site)
        self.assertEquals(204, r.status_code)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_remove_site_from_sitegroup(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        site = Site(username='test', id=100)
        responses.add(
            responses.DELETE, 'http://localhost/sitegroups/10/sites/rel/100', body='',
            status=204, match_querystring=True
        )

        r = SiteGroups.remove_site_from_sitegroup(self.token, sitegroup_id=sitegroup, site_id=site)
        self.assertEquals(204, r.status_code)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_get_sitegroup_view_config(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        resp = {'summaries': [{'aggregationType': 'LAST', 'assetType': 'TANK', 'label': 'Test', 'pointType': 'TOP_GAUGE', 'unit': 'feet'}]}
        responses.add(
            responses.GET, 'http://localhost/sitegroups/10/meta/viewconfig',
            json=resp, status=204, match_querystring=True
        )

        r = SiteGroups.get_sitegroup_view_config(self.token, sitegroup_id=sitegroup)
        self.assertIsInstance(r, SiteGroupViewConfig)
        summaries = r.summaries
        self.assertEquals(1, len(summaries))
        summary = summaries[0]
        self.assertIsInstance(summary, SiteGroupSummary)
        self.assertEquals('TANK', summary.asset_type)
        self.assertEquals('LAST', summary.aggregation_type)
        self.assertEquals('Test', summary.label)
        self.assertEquals('TOP_GAUGE', summary.point_type)
        self.assertEquals('feet', summary.unit)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_update_sitegroup_view_config(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        summary = SiteGroupSummary(aggregation_type='LAST', asset_type='TANK', label='Test', point_type='TOP_GAUGE', unit='feet')
        view_config = SiteGroupViewConfig(summaries=[summary, ])
        resp = {'summaries': [{'aggregationType': 'LAST', 'assetType': 'TANK', 'label': 'Test', 'pointType': 'TOP_GAUGE', 'unit': 'feet'}]}
        responses.add(
            responses.PUT, 'http://localhost/sitegroups/10/meta/viewconfig',
            json=resp, status=204, match_querystring=True
        )

        r = SiteGroups.update_sitegroup_view_config(self.token, sitegroup_id=sitegroup, view_config=view_config)
        self.assertIsInstance(r, SiteGroupViewConfig)
        summaries = r.summaries
        self.assertEquals(1, len(summaries))
        summary = summaries[0]
        self.assertIsInstance(summary, SiteGroupSummary)
        self.assertEquals('TANK', summary.asset_type)
        self.assertEquals('LAST', summary.aggregation_type)
        self.assertEquals('Test', summary.label)
        self.assertEquals('TOP_GAUGE', summary.point_type)
        self.assertEquals('feet', summary.unit)

    @attr('unit', 'sitegroups')
    @responses.activate
    def test_delete_sitegroup_view_config(self):
        sitegroup = SiteGroup(name='Test SiteGroup', id=10)
        responses.add(
            responses.DELETE, 'http://localhost/sitegroups/10/meta/viewconfig', body='',
            status=204, match_querystring=True
        )

        r = SiteGroups.delete_sitegroup_view_config(self.token, sitegroup_id=sitegroup)
        self.assertEquals(204, r.status_code)
