"""
Copyright 2013-2017 PhishMe, Inc.  All rights reserved.

This software is provided by PhishMe, Inc. ("PhishMe") on an "as is" basis and any express or implied warranties,
including but not limited to the implied warranties of merchantability and fitness for a particular purpose, are
disclaimed in all aspects.  In no event will PhishMe be liable for any direct, indirect, special, incidental or
consequential damages relating to the use of this software, even if advised of the possibility of such damage. Use of
this software is pursuant to, and permitted only in accordance with, the agreement between you and PhishMe.
"""


class Malware(object):
    """
    Malware class holds a single malware campaign.
    """

    def __init__(self, malware):
        """
        Initialize Malware object.
        """

        self.json = malware
        self.first_published = malware.get('firstPublished')
        self.last_published = malware.get('lastPublished')
        self.active_threat_report = malware.get('reportURL')
        self.active_threat_report_api = malware.get('apiReportURL')
        self.threathq_url = malware.get('threatDetailURL')
        self.threat_id = malware.get('id')
        self.label = malware.get('label')
        self.executiveSummary = malware.get('executiveSummary')
        self.brand = None
        self.malware_family = None
        self.block_set = None
        self.domain_set = None
        self.executable_set = None
        self.sender_ip_set = None
        self.spam_url_set = None
        self.subject_set = None
        self.sender_email_set = None

    @property
    def domain_set(self):
        """

        :return:
        """

        return self._domain_set

    @domain_set.setter
    def domain_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('domainSet'):
            return_list.append(self.DomainSet(item))

        self._domain_set = return_list

    @property
    def executable_set(self):
        """

        :return:
        """

        return self._executable_set

    @executable_set.setter
    def executable_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('executableSet'):
            return_list.append(self.ExecutableSet(item))

        self._executable_set = return_list

    @property
    def sender_ip_set(self):
        """

        :return:
        """

        return self._sender_ip_set

    @sender_ip_set.setter
    def sender_ip_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('senderIpSet'):
            return_list.append(self.SenderIPSet(item))

        self._sender_ip_set = return_list

    @property
    def sender_email_set(self):
        """

        :return:
        """

        return self._sender_email_set

    @sender_email_set.setter
    def sender_email_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('senderEmailSet'):
            return_list.append(self.SenderEmailSet(item))

        self._sender_email_set = return_list

    @property
    def subject_set(self):
        """

        :return:
        """

        return self._subject_set

    @subject_set.setter
    def subject_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('subjectSet'):
            return_list.append(self.SubjectSet(item))

        self._subject_set = return_list

    @property
    def spam_url_set(self):
        """

        :return:
        """

        return self._spam_url_set

    @spam_url_set.setter
    def spam_url_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('spamUrlSet'):
            return_list.append(self.SpamURLSet(item))

        self._spam_url_set = return_list

    @property
    def block_set(self):
        """

        :return:
        """

        return self._block_set

    @block_set.setter
    def block_set(self, value):
        """

        :param value:
        :return:
        """

        return_list = []

        for item in self.json.get('blockSet'):
            return_list.append(self.BlockSet(item))

        self._block_set = return_list

    @property
    def malware_family(self):
        """

        :param self:
        :return:
        """

        return self._malware_family

    @malware_family.setter
    def malware_family(self, value):
        """
        Return comma-separated list of malware families.

        :param value:
        :return:
        """

        if self.json.get('malwareFamilySet'):
            family_temp = []
            for family in self.json.get('malwareFamilySet'):
                family_temp.append(family.get('familyName'))
            self._malware_family = ', '.join(family_temp)
        else:
            self._malware_family = None

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

        if self.json.get('campaignBrandSet'):
            brand_temp = []
            for brand in self.json.get('campaignBrandSet'):
                brand_temp.append(brand.get('brand').get('text'))
            self._brand = ', '.join(brand_temp)
        else:
            self._brand = None

    class BlockSet(object):
        """
        BlockSet
        """

        default_value = 'Not recorded by PhishMe.'

        def __init__(self, block_set):
            """
            Initialize BlockSet object.

            :param block_set:
            :return:
            """

            self.json = block_set
            self.block_type = block_set.get('blockType')
            self.impact = block_set.get('impact')
            # Implement these at a future date.
            # self.severity = block_set.get('impact')
            # self.confidence = None
            self.role = block_set.get('role')
            self.role_description = block_set.get('roleDescription')
            self.malware_family = None
            self.malware_family_description = None
            self.watchlist_ioc = None
            self.watchlist_ioc_host = None
            self.watchlist_ioc_path = None

        @property
        def malware_family(self):
            """

            :param self:
            :return:
            """

            return self._malware_family

        @malware_family.setter
        def malware_family(self, value):
            """

            :param self:
            :return:
            """

            try:
                self._malware_family = self.json.get('malwareFamily').get('familyName')
            except AttributeError as exception:
                self._malware_family = None

        @property
        def malware_family_description(self):
            """

            :return:
            """

            return self._malware_family_description

        @malware_family_description.setter
        def malware_family_description(self, value):
            """

            :param self:
            :return:
            """

            try:
                self._malware_family_description = self.json.get('malwareFamily').get('description')
            except AttributeError as exception:
                self._malware_family_description = None

        @property
        def watchlist_ioc(self):
            """

            :return:
            """

            return self._watchlist_ioc

        @watchlist_ioc.setter
        def watchlist_ioc(self, value):
            """

            :param value:
            :return:
            """

            if self.block_type == 'URL':
                self._watchlist_ioc = self.json.get('data_1').get('url')
            else:
                self._watchlist_ioc = self.json.get('data_1')

        @property
        def watchlist_ioc_host(self):
            """

            :return:
            """

            return self._watchlist_ioc_host

        @watchlist_ioc_host.setter
        def watchlist_ioc_host(self, value):
            """

            :param value:
            :return:
            """

            if self.block_type == 'URL':
                self._watchlist_ioc_host = self.json.get('data_1').get('host')
            else:
                self._watchlist_ioc_host = None

        @property
        def watchlist_ioc_path(self):
            """

            :return:
            """

            return self._watchlist_ioc_path

        @watchlist_ioc_path.setter
        def watchlist_ioc_path(self, value):
            """

            :param value:
            :return:
            """

            if self.block_type == 'URL':
                self._watchlist_ioc_path = self.json.get('data_1').get('path')
            else:
                self._watchlist_ioc_path = None

    class DomainSet(object):
        """

        """

        def __init__(self, domain_set):
            """

            :return:
            """

            self.json = domain_set
            self.domain = domain_set.get('domain')
            self.total_count = domain_set.get('totalCount')

    class ExecutableSet(object):
        """
        ExecutableSet
        """

        default_value = 'Not recorded by PhishMe.'

        def __init__(self, executable_set):
            """
            Initialize ExecutableSet object
            """

            self.json = executable_set
            self.file_name = executable_set.get('fileName')
            self.type = executable_set.get('type')
            self.md5 = executable_set.get('md5Hex')
            self.sha1 = executable_set.get('sha1Hex')
            self.sha224 = executable_set.get('sha224Hex')
            self.sha256 = executable_set.get('sha256Hex')
            self.sha384 = executable_set.get('sha384Hex')
            self.sha512 = executable_set.get('sha512Hex')
            self.ssdeep = executable_set.get('ssdeep')
            self.malware_family = None
            self.malware_family_description = None
            self.subtype = None
            self.severity = None
            # Implement at a later date.
            # self.confidence = None

        @property
        def severity(self):
            """

            :param self:
            :return:
            """

            return self._severity

        @severity.setter
        def severity(self, value):
            """

            :param self:
            :return:
            """

            try:
                self._severity = self.json.get('severityLevel')
            except AttributeError as exception:
                self._severity = 'Major'

        @property
        def subtype(self):
            """

            :param self:
            :return:
            """

            return self._subtype

        @subtype.setter
        def subtype(self, value):
            """

            :param self:
            :return:
            """

            try:
                self._subtype = self.json.get('executableSubtype').get('description')
            except AttributeError as exception:
                self._subtype = None

        @property
        def malware_family(self):
            """

            :param self:
            :return:
            """

            return self._malware_family

        @malware_family.setter
        def malware_family(self, value):
            """

            :param self:
            :return:
            """

            try:
                self._malware_family = self.json.get('malwareFamily').get('familyName')
            except AttributeError as exception:
                self._malware_family = None

        @property
        def malware_family_description(self):
            """

            :return:
            """

            return self._malware_family_description

        @malware_family_description.setter
        def malware_family_description(self, value):
            """

            :param self:
            :return:
            """

            try:
                self._malware_family_description = self.json.get('malwareFamily').get('description')
            except AttributeError as exception:
                self._malware_family_description = None

    class SubjectSet(object):
        """
        SubjectSet
        """

        def __init__(self, subject_set):
            """
            Initialize SubjectSet object
            """

            self.json = subject_set
            self.subject = subject_set.get('subject')
            self.total_count = subject_set.get('totalCount')

    class SenderIPSet(object):
        """
        SenderIPSet
        """

        def __init__(self, sender_ip_set):
            """
            Initialize SenderIPSet object
            """

            self.json = sender_ip_set
            self.ip = sender_ip_set.get('ip')
            self.total_count = sender_ip_set.get('totalCount')

    class SenderEmailSet(object):
        """
        SenderEmailSet
        """

        def __init__(self, sender_email_set):
            """
            Initialize SenderEmailSet object
            """

            self.json = sender_email_set
            self.sender_email = sender_email_set.get('senderEmail')
            self.total_count = sender_email_set.get('totalCount')

    class SpamURLSet(object):
        """

        """

        def __init__(self, spam_url_set):
            """

            :return:
            """

            self.json = spam_url_set
            self.url = URL(spam_url_set.get('url_1'))
            self.total_count = spam_url_set.get('totalCount')


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
