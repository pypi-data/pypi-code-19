class OnyxErpService(object):

    __api_root = str()

    def get_api_root(self):
        return self.__api_root

    def set_api_root(self, api_root):
        self.__api_root  = api_root
        return self
