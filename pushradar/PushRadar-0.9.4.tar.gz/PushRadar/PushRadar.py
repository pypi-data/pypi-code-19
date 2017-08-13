import json
from .PushRadarUtils import PushRadarUtils
from .PushRadarClassInstances import PushRadarClassInstances
from .PushRadarAPIClient import PushRadarAPIClient


class PushRadar:
    """ A realtime push notifications API service for the web, featuring advanced targeting. """

    # ------------------------------
    # Initialisation & configuration 
    # ------------------------------  

    # The dictionary of data items to broadcast
    __data = {}

    # The list of user identifiers to target
    __target_user_ids = []

    # The list of action identifiers to target
    __target_actions = []

    # The list of "not" action identifiers to target
    __target_not_actions = []

    # The list of browsers to target
    __target_browsers = []

    # The list of countries to target (as ISO 3166-1 alpha-2 country codes)
    __target_countries = []

    # The list of continents to target (as two-letter continent codes)
    __target_continents = []

    # The list of IP addresses to target
    __target_ips = []

    # Specifies whether we are currently in unit testing mode
    __is_unit_test_mode = False

    def __init__(self, api_secret):
        """ Creates a new instance of PushRadar with the specified API secret. """
        # Reset the targeting options
        self.reset_targeting()
        # Trim the API secret
        api_secret = api_secret.strip()
        # If we are running unit tests, set the unit test mode flag and skip the PushRadar API client initialisation
        self.__is_unit_test_mode = (api_secret == "test-secret")
        # Check that the API secret starts with sk_
        if not api_secret.startswith("sk_"):
            raise ValueError("API secret invalid. You can view your PushRadar API secret "
                             "at https://dashboard.pushradar.com/api")
        # Make a new instance of a PushRadar API client with the specified API secret
        client = PushRadarAPIClient(api_secret)
        PushRadarClassInstances.api_client = client

    # ------------------------------
    # Browser targeting
    # ------------------------------

    def target_browser(self, browser):
        """ Targets the notification to clients currently using the given browser. """
        # Trim the browser and convert it to lowercase
        browser = browser.strip().lower()
        # Validate the browser for being one of the supported types
        if not any(browser in s for s in ["chrome", "ie", "edge", "safari", "opera", "firefox"]):
            raise ValueError("The browser must be one of the following: 'chrome', 'ie', "
                             "'edge', 'safari', 'opera', 'firefox'.")
        # Add the browser to the list
        if browser not in self.__target_browsers:
            self.__target_browsers.append(browser)
        # Allow method chaining
        return self

    def target_browsers(self, *browsers):
        """ Targets the notification to clients currently using any of the given browsers. """
        # Target each browser
        for x in browsers:
            self.target_browser(x)
        # Allow method chaining
        return self

    # ------------------------------
    # Country targeting
    # ------------------------------

    def target_country(self, country_code):
        """ Targets the notification to clients currently located in the given country. """
        # Trim the country code and convert it to uppercase
        country_code = country_code.strip().upper()
        # Ensure that the country code is not empty
        if country_code == "":
            raise ValueError("The country code provided cannot be empty.")
        # Validate the country code
        if country_code not in PushRadarUtils.get_countries().keys():
            raise ValueError("The country code provided must be a valid two-letter "
                             "(ISO 3166-1 alpha-2) code.")
        # Add the country to the list
        if country_code not in self.__target_countries:
            self.__target_countries.append(country_code)
        # Allow method chaining
        return self

    def target_countries(self, *country_codes):
        """ Targets the notification to clients currently located in any of the given countries. """
        # Target each county
        for x in country_codes:
            self.target_country(x)
        # Allow method chaining
        return self

    # ------------------------------
    # Continent targeting
    # ------------------------------

    def target_asia(self):
        """ Targets the notification to clients currently located in Asia. """
        # Target the continent
        self._target_continent("AS")
        # Allow method chaining
        return self

    def target_africa(self):
        """ Targets the notification to clients currently located in Africa. """
        # Target the continent
        self._target_continent("AF")
        # Allow method chaining
        return self

    def target_antarctica(self):
        """ Targets the notification to clients currently located in Antarctica. """
        # Target the continent
        self._target_continent("AN")
        # Allow method chaining
        return self

    def target_europe(self):
        """ Targets the notification to clients currently located in Europe. """
        # Target the continent
        self._target_continent("EU")
        # Allow method chaining
        return self

    def target_north_america(self):
        """ Targets the notification to clients currently located in North America. """
        # Target the continent
        self._target_continent("NA")
        # Allow method chaining
        return self

    def target_south_america(self):
        """ Targets the notification to clients currently located in South America. """
        # Target the continent
        self._target_continent("SA")
        # Allow method chaining
        return self

    def target_oceania(self):
        """ Targets the notification to clients currently located in Oceania. """
        # Target the continent
        self._target_continent("OC")
        # Allow method chaining
        return self

    def _target_continent(self, continent_code):
        """ Targets a continent by its continent code. """
        # Target the countries located in this continent
        for country in PushRadarUtils.get_countries_from_continent(continent_code):
            self.target_country(country)
        # Add the continent code to the list
        if continent_code not in self.__target_continents:
            self.__target_continents.append(continent_code)

    # ------------------------------
    # IP address targeting
    # ------------------------------

    def target_ip(self, ip_address):
        """ Targets the notification to clients with the given IP address. """
        # Trim the IP address
        ip_address = ip_address.strip()
        # Make sure that the IP address is not empty
        if ip_address == "":
            raise ValueError("The IP address provided cannot be empty.")
        # Check for wildcard IPs
        if "*" in ip_address:
            raise ValueError("Wildcard IP address targeting is not supported.")
        # Validate the IP address
        if not PushRadarUtils.is_valid_ip(ip_address):
            raise ValueError("The IP address provided must be a valid IPv4 or IPv6 address.")
        # Add the IP address to the list
        if ip_address not in self.__target_ips:
            self.__target_ips.append(ip_address)
        # Allow method chaining
        return self

    def target_ips(self, *ip_addresses):
        """ Targets the notification to clients with any of the given IP addresses. """
        # Target the IP addresses
        for x in ip_addresses:
            self.target_ip(x)
        # Allow method chaining
        return self

    # ------------------------------
    # Action targeting
    # ------------------------------

    def target_action(self, action_identifier):
        """ Targets the notification to clients who have taken the given action. """
        # Trim the action identifier
        action_identifier = action_identifier.strip()
        # Make sure that the action identifier is not empty
        if action_identifier == "":
            raise ValueError("The action identifier cannot be empty.")
        # Make sure that the action is not in the target "not" actions list
        if action_identifier in self.__target_not_actions:
            raise RuntimeError("Action '" + action_identifier + "' is already in the 'not' actions list.")
        # Add the action to the list
        if action_identifier not in self.__target_actions:
            self.__target_actions.append(action_identifier)
        # Allow method chaining
        return self

    def target_actions(self, *action_identifiers):
        """ Targets the notification to clients who have taken any of the given actions. """
        # Target the actions
        for x in action_identifiers:
            self.target_action(x)
        # Allow method chaining
        return self

    def target_not_action(self, action_identifier):
        """ Targets the notification to clients who have not taken the given action. """
        # Trim the action identifier
        action_identifier = action_identifier.strip()
        # Make sure that the action identifier is not empty
        if action_identifier == "":
            raise ValueError("The action identifier cannot be empty.")
        # Make sure that the action is not in the target actions list
        if action_identifier in self.__target_actions:
            raise RuntimeError("Action '" + action_identifier + "' is already in the actions list.")
        # Add the action to the list
        if action_identifier not in self.__target_not_actions:
            self.__target_not_actions.append(action_identifier)
        # Allow method chaining
        return self

    def target_not_actions(self, *action_identifiers):
        """ Targets the notification to clients who have not taken any of the given actions. """
        # Target the actions
        for x in action_identifiers:
            self.target_not_action(x)
        # Allow method chaining
        return self

    # ------------------------------
    # User targeting
    # ------------------------------

    def target_user(self, user_id):
        """ Targets the notification to a specific user (identifier by their user ID). """
        # Make sure that the user ID is not None
        if user_id is None:
            raise ValueError("The user ID cannot be None.")
        # Add the user ID to the list
        if user_id not in self.__target_user_ids:
            self.__target_user_ids.append(user_id)
        # Allow method chaining
            return self

    def target_users(self, *user_ids):
        """ Targets the notification to specific users (identifier by their user IDs). """
        # Target the user IDs
        for x in user_ids:
            self.target_user(x)
        # Allow method chaining
        return self

    # ------------------------------
    # Adding data
    # ------------------------------

    def add_data_item(self, key, value):
        """ Adds a data item to the list of data items. """
        # Trim the key
        key = key.strip()
        # Make sure the key is not empty
        if key == "":
            raise ValueError("The key provided cannot be empty.")
        # Add the data item to the dictionary
        if key not in self.__data.keys():
            self.__data[key] = value
        # Allow method chaining
        return self

    def add_data_items(self, **kwargs):
        """ Adds multiple data items to the list of data items. """
        # Add the data items
        for x in kwargs:
            self.add_data_item(x, kwargs[x])
        # Allow method chaining
        return self

    # ------------------------------
    # Broadcast method
    # ------------------------------

    def broadcast(self, channel, **kwargs):
        """ Broadcasts data on the channel specified. """
        # If we are running unit tests, throw an exception
        if self.__is_unit_test_mode:
            raise NotImplementedError("Unit testing of the broadcast() method is not supported.")
        # Trim the channel name
        channel = channel.strip()
        # Check whether data has been provided
        if len(kwargs) == 0 and len(self.__data) == 0:
            raise ValueError("There is no data to broadcast.")
        # Check whether the channel name contains spaces
        if " " in channel:
            raise ValueError("The channel name cannot contain spaces. By convention, channel names are alphanumerical "
                             "and lowercase, with optional dashes (e.g. 'test-channel').")
        # Use the stored data if the kwargs parameter is empty
        if len(kwargs) == 0:
            kwargs = self.__data
        # Initialize the dictionary of data to send to the server
        data_to_send = {
            "channel": channel,
            "notification": json.dumps(kwargs),
            "target_user_ids": json.dumps(self.__target_user_ids),
            "target_actions": json.dumps(self.__target_actions),
            "target_not_actions": json.dumps(self.__target_not_actions),
            "target_continents": json.dumps(self.__target_continents),
            "target_countries": json.dumps(self.__target_countries),
            "target_ips": json.dumps(self.__target_ips),
            "target_browsers": json.dumps(self.__target_browsers)
        }
        # Get the PushRadar API client
        client = PushRadarClassInstances.api_client
        # Broadcast the notification
        response = client.post("/broadcast", data_to_send)
        # Reset the targeting options
        self.reset_targeting()
        # Return the response
        return response

    # ------------------------------
    # Resetting targeting options
    # ------------------------------

    def reset_targeting(self):
        """ Resets the targeting options. """
        self.__data = {}
        self.__target_actions = []
        self.__target_not_actions = []
        self.__target_browsers = []
        self.__target_continents = []
        self.__target_countries = []
        self.__target_ips = []
        self.__target_user_ids = []
