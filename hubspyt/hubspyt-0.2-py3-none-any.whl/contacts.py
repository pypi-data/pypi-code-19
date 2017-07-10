"""Contacts API endpoint wrapper"""

import requests

from hubspyt.base_wrapper import BaseWrapper
from hubspyt.models.contact import Contact

class Contacts(BaseWrapper):
    """Wrapper for the contacts endpoint"""

    def _contacts_url(self, addon):
        """Adds an addon URL to the base Contacts url"""

        contacts_url = self.contacts_base_url

        url = '{contacts_url}{addon}'.format(contacts_url=contacts_url, addon=addon)

        return url

    def all(self, count=None):
        """Fetches all current contacts with an optional count"""

        contacts_all_url = self.contacts_all_url
        contact_list = []

        if count is None:
            has_more = True
            vid_offset = None

            while has_more is True:
                url = self._get_url(
                    self._contacts_url(contacts_all_url),
                    [
                        {'name': 'count', 'value': 250},
                        {'name': 'vidOffset', 'value': vid_offset},
                    ],
                )

                response = requests.get(url).json()
                contacts = response.get('contacts')

                if response.get('has-more') is False:
                    has_more = False

                vid_offset = response.get('vid-offset')

                print(vid_offset)

                for item in contacts:
                    vid = item.get('vid')
                    first_name = None
                    last_name = None
                    company = None

                    if item.get('properties').get('firstname'):
                        first_name = item.get('properties').get('firstname').get('value')

                    if item.get('properties').get('lastname'):
                        last_name = item.get('properties').get('lastname').get('value')

                    if item.get('properties').get('company'):
                        company = item.get('properties').get('company').get('value')

                    contact = Contact(
                        vid=vid,
                        first_name=first_name,
                        last_name=last_name,
                        company=company,
                    )

                    contact_list.append(contact)
        else:
            url = self._get_url(self._contacts_url(contacts_all_url))

            response = requests.get(url).json()
            contacts = response.get('contacts')

            for item in contacts:
                vid = item.get('vid')
                first_name = None
                last_name = None
                company = None

                if item.get('properties').get('firstname'):
                    first_name = item.get('properties').get('firstname').get('value')

                if item.get('properties').get('lastname'):
                    last_name = item.get('properties').get('lastname').get('value')

                if item.get('properties').get('company'):
                    company = item.get('properties').get('company').get('value')

                contact = Contact(
                    vid=vid,
                    first_name=first_name,
                    last_name=last_name,
                    company=company,
                )

                contact_list.append(contact)

        return contact_list

    def batch_modify(self, modified):
        """Send HubSpot's API modified/created contacts"""

        contacts_batch_url = self.contacts_batch_url
        url = self._get_url(self._contacts_url(contacts_batch_url))

        modified_list = []

        for contact in modified:
            modified_list.append(contact.get_update())

        response = requests.post(url, json=modified_list)
        status = response.status_code

        if status == 202:
            return True

        print(status, response.json())

        return False
