import logging

from dxlbootstrap.app import Application
from dxlclient.service import ServiceRegistrationInfo
from requesthandlers import *


# Configure local logger
logger = logging.getLogger(__name__)


class UrlVoidApiService(Application):
    """
    The "URLVoid DXL Service" application class.
    """

    #: The name of the "General" section within the application configuration file
    GENERAL_CONFIG_SECTION = "General"

    #: The property used to specify the URLVoid API Key in the application
    #: configuration file
    GENERAL_API_KEY_CONFIG_PROP = "apiKey"

    #: The DXL service type for the URLVoid API
    SERVICE_TYPE = "/opendxl-urlvoid/service/urlvapi"

    #: The length of the DXL service type string
    SERVICE_TYPE_LENGTH = len(SERVICE_TYPE)

    #: The URL format for URLVoid API invocations
    URL_VOID_API_URL_FORMAT = "http://api.urlvoid.com/api1000/{0}/"

    #: The "host info" command
    CMD_HOST_INFO = "host/info"

    #: The "host info" DXL request topic
    REQ_TOPIC_HOST_INFO = "{0}/{1}".format(SERVICE_TYPE, CMD_HOST_INFO)

    #: The "host rescan" command
    CMD_HOST_RESCAN = "host/rescan"

    #: The "host rescan" DXL request topic
    REQ_TOPIC_HOST_RESCAN = "{0}/{1}".format(SERVICE_TYPE, CMD_HOST_RESCAN)

    #: The "host scan" command
    CMD_HOST_SCAN = "host/scan"

    #: The "host new scan" DXL request topic
    REQ_TOPIC_HOST_SCAN = "{0}/{1}".format(SERVICE_TYPE, CMD_HOST_SCAN)

    #: The "stats remained" command
    CMD_STATS_REMAINED = "stats/remained"

    #: The "stats remained" DXL request topic
    REQ_TOPIC_STATS_REMAINED = "{0}/{1}".format(SERVICE_TYPE, CMD_STATS_REMAINED)

    def __init__(self, config_dir):
        """
        Constructor parameters:

        :param config_dir: The location of the configuration files for the
            application
        """
        super(UrlVoidApiService, self).__init__(config_dir, "dxlurlvoidservice.config")
        self._api_key = None

    @property
    def api_key(self):
        """
        The URLVoid API key
        """
        return self._api_key

    @property
    def client(self):
        """
        The DXL client used by the application to communicate with the DXL
        fabric
        """
        return self._dxl_client

    @property
    def config(self):
        """
        The application configuration (as read from the "dxlurlvoidservice.config" file)
        """
        return self._config

    def on_run(self):
        """
        Invoked when the application has started running.
        """
        logger.info("On 'run' callback.")

    def on_load_configuration(self, config):
        """
        Invoked after the application-specific configuration has been loaded

        This callback provides the opportunity for the application to parse
        additional configuration properties.

        :param config: The application configuration
        """
        logger.info("On 'load configuration' callback.")

        # API Key
        try:
            self._api_key = config.get(self.GENERAL_CONFIG_SECTION, self.GENERAL_API_KEY_CONFIG_PROP)
        except Exception:
            pass
        if not self._api_key:
            raise Exception("URLVoid API Key not found in configuration file: {0}"
                            .format(self._app_config_path))

    def on_dxl_connect(self):
        """
        Invoked after the client associated with the application has connected
        to the DXL fabric.
        """
        logger.info("On 'DXL connect' callback.")
    
    def on_register_services(self):
        """
        Invoked when services should be registered with the application
        """
        # Register service 'urlvapi'
        logger.info("Registering service: {0}".format("urlvoidservice"))
        service = ServiceRegistrationInfo(self._dxl_client, self.SERVICE_TYPE)

        logger.info("Registering request callback: {0}".format(self.CMD_HOST_INFO))
        self.add_request_callback(
                service, self.REQ_TOPIC_HOST_INFO,
                UrlVoidApiCallback(self, [UrlVoidApiCallback.PARAM_HOST]), False)

        logger.info("Registering request callback: {0}".format(self.CMD_HOST_RESCAN))
        self.add_request_callback(
                service, self.REQ_TOPIC_HOST_RESCAN,
                UrlVoidApiCallback(self, [UrlVoidApiCallback.PARAM_HOST]), False)

        logger.info("Registering request callback: {0}".format(self.CMD_HOST_SCAN))
        self.add_request_callback(
                service, self.REQ_TOPIC_HOST_SCAN,
                UrlVoidApiCallback(self, [UrlVoidApiCallback.PARAM_HOST]), False)

        logger.info("Registering request callback: {0}".format(self.CMD_STATS_REMAINED))
        self.add_request_callback(
                service, self.REQ_TOPIC_STATS_REMAINED, UrlVoidApiCallback(self), False)

        self.register_service(service)
