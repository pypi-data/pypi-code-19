import unittest
from apprenda_account_client import ApprendaAccountClient

class TestAccountSubscriptions(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_getAccountSubscriptions(self):
        client = self.get_client()

        apps = client.get_applications()
        self.assertIsNotNone(apps)

        for app in apps:
            subs = client.get_subscriptions(app.application_alias, app.version_alias)

            self.assertIsNotNone(subs)

    def test_get_plans(self):
        client = self.get_client()

        apps = client.get_applications()
        self.assertIsNotNone(apps)

        app = None
        for eachApp in apps:
            app = eachApp
            break

        plans = client.get_plans(app.application_alias, app.version_alias)
        self.assertIsNotNone(plans)

        for plan in plans:
            by_id = client.get_plan(app.application_alias, app.version_alias, plan.id)
            self.assertIsNotNone(by_id)
            self.assertEqual(plan.name, by_id.name)

    def test_create_subscriptions(self):
        client = self.get_client()

        apps = client.get_applications()
        self.assertIsNotNone(apps)

        app = None
        for eachApp in apps:
            app = eachApp
            break

        plans = client.get_plans(app.application_alias, app.version_alias)
        self.assertIsNotNone(plans)

        plan = None
        for eachPlan in plans:
            plan = eachPlan
            break

        reqs = {plan.id: 2}
        client.create_subscriptions(app.application_alias, app.version_alias, reqs)

        subs = client.get_subscriptions(app.application_alias, app.version_alias)

        self.assertIsNotNone(subs)
        self.assertGreaterEqual(len(subs), 2)

    @staticmethod
    def get_client():
        return ApprendaAccountClient('https://apps.apprenda.msterling10', "gsterling@apprenda.com", "password")
