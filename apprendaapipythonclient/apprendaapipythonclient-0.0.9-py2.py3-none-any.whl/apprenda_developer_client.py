from apprendaapipythonclient.apprenda_api_client import ApprendaAPIClient


class ApprendaDeveloperClient(ApprendaAPIClient):
    def __init__(self, config):
        super(ApprendaDeveloperClient, self).__init__(config.host, "developer", config.username, config.password)

    # def get_applications(self):
    #     api = AppsApi(self.internalClient)
    #     apps = api.apps_get_all()
    #
    #     return apps
    #
    # def get_application(self, app_alias):
    #     api = AppsApi(self.internalClient)
    #     app = api.apps_get(app_alias)
    #
    #     return app
