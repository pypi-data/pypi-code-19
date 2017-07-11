from apprendaapipythonclient.apprenda_api_client import ApprendaAPIClient
from apprendaapipythonclient.rest import ApiException
from apprendaapipythonclient.apis.soc import AddOnsApi
from apprendaapipythonclient.apis.soc import ApplicationsApi
from apprendaapipythonclient.apis.soc import CloudsApi
from apprendaapipythonclient.apis.soc import CustomPropertiesApi
from apprendaapipythonclient.apis.soc import HostsApi
from apprendaapipythonclient.apis.soc import NodesApi
from apprendaapipythonclient.apis.soc import RegistryApi
from apprendaapipythonclient.models.soc.registry_setting import RegistrySetting

from apprendaapipythonclient.apis.soc import WorkloadsApi


class ApprendaSOCClient(ApprendaAPIClient):
    # how many applications to pull down per request
    apps_page_size = 20
    custom_properties_page_size = 20
    nodes_page_size = 500
    default_page_size = 20

    def __init__(self, config):
        super(ApprendaSOCClient, self).__init__(config.host, "soc", config.username, config.password)

    """
    Get all applications currently hosted by the platform, or just one by alias
    """
    def get_applications(self, alias=None):
        api = ApplicationsApi(self.internalClient)
        if alias is None:
            depager = self.get_depager(api.apps_search_new, self.apps_page_size)
            return depager.next()
        else:
            try:
                return api.get_app_by_alias(alias)
            except ApiException:
                raise KeyError('The application ' + alias + " could not be found")

    """
    Get all custom properties, or one by name
    """
    def get_custom_properties(self, name=None):
        api = CustomPropertiesApi(self.internalClient)

        depager = self.get_depager(api.custom_properties_get_public, self.custom_properties_page_size)
        if name is None:
            return depager.next()
        else:
            for prop in depager.next():
                if prop.name == name:
                    return prop

            raise KeyError('The custom property does not exist')

    def add_custom_property(self, custom_property):
        api = CustomPropertiesApi(self.internalClient)

        return api.add_custom_property(custom_property)

    def remove_custom_property(self, custom_property_id):
        api = CustomPropertiesApi(self.internalClient)
        return api.custom_properties_remove(custom_property_id)

    def transition_node(self, node, newstate):
        if node is None or newstate is None:
            raise Exception('Please provide the name of the node to update and the new state')
        api = HostsApi(self.internalClient)
        response = api.put_api_v1_hosts_host_name_state(node, newstate)
        if response.status_code == 204:
            return True
        elif response.status_code == 404:
            raise KeyError(
                'The node provided was not found. Please ensure that the information passed is correct and try again.')
        else:
            raise Exception('Unknown error when setting the node state for: ' + node)

    def get_nodes(self):
        api = NodesApi(self.internalClient)

        depager = self.get_depager(api.get_all_nodes, self.nodes_page_size)
        return depager.next()

    def get_add_ons(self, alias=None):
        api = AddOnsApi(self.internalClient)

        if alias is None:
            container = api.add_on_get()
            return container.items
        else:
            try:
                res = api.add_on_get_by_name(alias)
                if res is None:
                    raise KeyError("AddOn " + alias + " was not found")
                return res
            except ApiException:
                raise KeyError('AddOn ' + alias + " was not found")

    def get_public_clouds(self, id=None):
        api = CloudsApi(self.internalClient)

        if id is None:
            container = api.clouds_get_public()
            return container.items
        else:
            try:
                res = api.clouds_get_by_id_p_ublic(id)
                if res is None:
                    raise KeyError("Cloud " + str(id) + " was not found")
                return res
            except ApiException:
                raise KeyError("Cloud " + str(id) + " was not found")

    def get_registry_settings(self):
        api = RegistryApi(self.internalClient)

        depager = self.get_depager(api.registry_get, 20)
        return depager.next()

    def get_registry_setting(self, name):
        api = RegistryApi(self.internalClient)

        return api.registry_get_by_name(name)

    def create_registry_setting(self, name, value, encrypted = False, readonly = False):
        setting = RegistrySetting(name = name, value = value, is_encrypted=encrypted, is_read_only=readonly)

        api = RegistryApi(self.internalClient)
        return api.registry_post_new(setting)

    def delete_registry_settting(self, name):
        api = RegistryApi(self.internalClient)

        return api.registry_delete(name)

    def get_workloads_on_node(self, node_name):
        api = WorkloadsApi(self.internalClient)
        res = api.get_workloads_on_node(node_name)

        if res is None:
            return None

        return res.items
