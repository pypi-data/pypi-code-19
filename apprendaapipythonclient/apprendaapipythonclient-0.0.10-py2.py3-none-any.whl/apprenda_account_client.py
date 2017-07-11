from apprendaapipythonclient.apis.account.application_versions_api import ApplicationVersionsApi
from apprendaapipythonclient.apis.account.roles_api import RolesApi
from apprendaapipythonclient.apis.account.subscriptions_api import SubscriptionsApi
from apprendaapipythonclient.apis.account.users_api import UsersApi

from apprendaapipythonclient.apprenda_api_client import ApprendaAPIClient
from apprendaapipythonclient.apis.account.plans_api import PlansApi
from apprendaapipythonclient.models.account import PlanRequest
from apprendaapipythonclient.models.account import Role
from apprendaapipythonclient.models.account import SubscriptionRequest
from apprendaapipythonclient.models.account import User


class ApprendaAccountClient(ApprendaAPIClient):
    def __init__(self, config):
        super(ApprendaAccountClient, self).__init__(config.host, "account", config.username, config.password)

    def get_applications(self):
        api = ApplicationVersionsApi(self.internalClient)

        depager = self.get_depager(api.api_v1_application_versions_get, 20)
        return depager.next()

    def get_subscriptions(self, app_alias, version_alias):
        key = self.get_app_version_key(app_alias, version_alias)

        res = self.get_subscriptions_by_key(key)

        if res is None:
            return None

        return res.items

    def get_subscriptions_by_key(self, app_version_key):
        api = SubscriptionsApi(self.internalClient)

        return api.api_v1_application_versions_application_version_key_subscriptions_get(app_version_key)

    def get_plans(self, app_alias, version_alias):
        key = self.get_app_version_key(app_alias, version_alias)
        api = PlansApi(self.internalClient)

        res = api.api_v1_application_versions_application_version_key_plans_get(key)
        if res is None:
            return None

        return res.items

    def get_plan(self, app_alias, version_alias, plan_id):
        key = self.get_app_version_key(app_alias, version_alias)
        api = PlansApi(self.internalClient)

        return  api.api_v1_application_versions_application_version_key_plans_plan_id_get(key, plan_id)

    def create_subscriptions(self, app_alias, version_alias, plan_id_and_numbers):
        key = self.get_app_version_key(app_alias, version_alias)
        plan_reqs = []

        for plan_id in plan_id_and_numbers:
            plan_req = PlanRequest(plan_id, plan_id_and_numbers[plan_id])
            plan_reqs.append(plan_req)

        sub_request = SubscriptionRequest(plan_reqs)

        api = SubscriptionsApi(self.internalClient)

        return api.api_v1_application_versions_application_version_key_subscriptions_post(key,
                                                                                          body=sub_request)

    def get_roles(self):
        '''
        Get all roles in the system
        :return:
        '''
        api = RolesApi(self.internalClient)

        res = api.api_v1_roles_get()
        if res is None:
            return None

        return res.items

    def create_role(self, name, description):
        role = Role(name= name, description=description)
        api = RolesApi(self.internalClient)

        return api.api_v1_roles_post(body=role)

    def get_role(self, role_id):
        api = RolesApi(self.internalClient)
        res = api.api_v1_roles_role_id_get(role_id)
        return res

    def delete_role(self, role_id):
        api = RolesApi(self.internalClient)
        return api.api_v1_roles_role_id_roles_delete(role_id)

    def get_users(self):
        api = UsersApi(self.internalClient)

        depager = self.get_depager(api.api_v1_users_get, 20)
        return depager.next()

    # def get_user(self, user_id):
    #     api = UsersApi(self.internalClient)
    #     api.api_v1_users_get(user_id=user_id)

    def create_user(self, first_name, last_name, email, identifier, is_enabled):
        user = User(first_name=first_name, last_name=last_name, email=email, identifier=identifier,
                    is_enabled=is_enabled)

        api = UsersApi(self.internalClient)
        return api.api_v1_users_post(body=user)

    def delete_user(self, user_id):
        api = UsersApi(self.internalClient)
        return api.api_v1_users_delete(user_id=user_id)

    def get_users_assigned_to_role(self, role_id):
        api = RolesApi(self.internalClient)

        res = api.api_v1_roles_role_id_users_get(role_id)

        if res is None:
            return None

        return res.items

    def add_users_to_role(self, role_id, user_ids):
        api = RolesApi(self.internalClient)

        return api.api_v1_roles_role_id_users_post(role_id, body=user_ids)

    def remove_users_from_role(self, role_id, user_ids):
        api = RolesApi(self.internalClient)

        return api.api_v1_roles_role_id_users_delete(role_id, body=user_ids)

    @staticmethod
    def get_app_version_key(app_alias, version_alias):
        return app_alias + "-" + version_alias
