"""
Copyright 2013-2017 PhishMe, Inc.  All rights reserved.

This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
"""


class Phish(object):
    """
    Phish class holds a single phish campaign.
    """
    def __init__(self, phish):
        """
        Initialize Phish object.
        """

        self.json = phish

        self.confirmed_date = phish.get('confirmedDate')
        self.first_published = phish.get('firstDate')
        self.last_published = phish.get('lastDate')
        self.threathq_url = phish.get('threatDetailURL')
        self.threat_id = phish.get('id')
        self.web_components = phish.get('webComponents')
        self.kits = phish.get('kits')
        self.title = phish.get('title')
        self.reported_url_list = None
        self.phish_url = None
        self.action_url_list = None
        self.screenshot_url = None
        self.brand = None
        self.ip = None

    @property
    def ip(self):
        """

        :return:
        """

        return self._ip

    @ip.setter
    def ip(self, value):
        """

        :param value:
        :return:
        """

        if self.json.get('ipDetail'):
            self._ip = IPv4(self.json.get('ipDetail'))
        else:
            self._ip = None

    @property
    def phish_url(self):
        """

        :return:
        """

        return self._phish_url

    @phish_url.setter
    def phish_url(self, value):
        """

        :param value:
        :return:
        """

        if self.json.get('phishingURL_1'):
            self._phish_url = URL(self.json.get('phishingURL_1'))
        else:
            self._phish_url = None

    @property
    def screenshot_url(self):
        """

        :return:
        """

        return self._screenshot_url

    @screenshot_url.setter
    def screenshot_url(self, value):
        """

        :param value:
        :return:
        """

        try:
            self._screenshot_url = URL(self.json.get('screenshot').get('url_1')).url

        # If we catch a PmAttributeError here, we miss the AttributeError being thrown when a screenshot URL is not available.
        except AttributeError as exception:
            self._screenshot_url = None

    @property
    def reported_url_list(self):
        """

        :return:
        """

        return self._reported_url_list

    @reported_url_list.setter
    def reported_url_list(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('reportedURLs_1'):
            return_list.append(URL(item))

        self._reported_url_list = return_list

    @property
    def action_url_list(self):
        """

        :return:
        """

        return self._action_url_list

    @action_url_list.setter
    def action_url_list(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('actionURLs_1'):
            return_list.append(URL(item))

        self._action_url_list = return_list

    @property
    def brand(self):
        """

        :return:
        """

        return self._brand

    @brand.setter
    def brand(self, value):
        """
        Return comma-separated list of brands.
        """
        brand_temp = []

        if self.json.get('brands'):
            for brand in self.json.get('brands'):
                brand_temp.append(brand.get('text'))

            self._brand = ', '.join(brand_temp)

        else:
            self._brand = None


class IPv4(object):
    """

    """

    def __init__(self, ipv4):
        """

        :return:
        """
        if ipv4:
            self.json = ipv4
            self.asn = ipv4.get('asn')
            self.asn_organization = ipv4.get('asnOrganization')
            self.continent_code = ipv4.get('continentCode')
            self.continent_name = ipv4.get('continentName')
            self.country_iso_code = ipv4.get('countryIsoCode')
            self.country_name = ipv4.get('countryName')
            self.ip = ipv4.get('ip')
            self.isp = ipv4.get('isp')
            self.latitude = ipv4.get('latitude')
            self.longitude = ipv4.get('longitude')
            self.lookup_on = ipv4.get('lookupOn')
            self.metro_code = ipv4.get('metroCode')
            self.organization = ipv4.get('organization')
            self.postal_code = ipv4.get('postalCode')
            self.subdivision_name = ipv4.get('subdivisionName')
            self.subdivision_iso_code = ipv4.get('subdivisionIsoCode')
            self.time_zone = ipv4.get('timeZone')
            self.user_type = ipv4.get('userType')

    def __getattr__(self, item):
        return None


class URL(object):
    """

    """

    def __init__(self, url):
        """

        :param url:
        :return:
        """

        self.json = url
        self.domain = url.get('domain')
        self.host = url.get('host')
        self.path = url.get('path')
        self.protocol = url.get('protocol')
        self.query = url.get('query')
        self.url = url.get('url')

    def __getattr__(self, item):
            return None
