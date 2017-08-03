import re
import logging
import datetime
import json
import time

from bs4 import BeautifulSoup

from .api_adapter import ApiAdapter


class ApiClient(object):
    def __init__(self, username=None, password=None):
        self.adapter = ApiAdapter(username, password)
        self.logger = logging.getLogger(__name__)

    def is_admin(self):
        resp = self.adapter.get(
            endpoint='MyPC/Front.aspx',
            params={
                'page': 'header'
            }
        )

        soup = BeautifulSoup(resp.text, 'html.parser')
        return 'menuItemAdmin' in [match.get('id') for match in soup.find_all('a', attrs={'class': 'menu'})]

    def all_resource_status(self, site_id=None):
        endpoint = 'MyPC/Front.aspx?page=getResourceStatesAPI&siteId={site_id}'.format(
            site_id=site_id if site_id else ''
        )
        resp = self.adapter.get(endpoint=endpoint)

        return self._to_json(resp.text)

    def admin_all_resource_status(self, site_id=None):
        all_status = self.all_resource_status(site_id)

        for site in all_status:
            for location in site['locations']:
                admin_resource_status = self.admin_location_status(location['id'])
                for resource in location['resources']:
                    resource_id = resource['id']
                    admin_status = admin_resource_status[resource_id]['state']
                    resource['admin_status'] = admin_status
                # Rate limit or the server hates us
                time.sleep(0.1)

        return all_status

    def admin_location_status(self, location_id):
        endpoint = 'MyPC/Front.aspx?page=adminItems&itemType=resource&parentId={location_id}'.format(
            location_id=location_id
        )
        resp = self.adapter.get(endpoint=endpoint)

        soup = BeautifulSoup(resp.text, 'html.parser')
        matches = soup.find_all('div', attrs={'class': 'adminItem'})

        resources = {}
        for match in matches:
            match_id = match.get('id')
            match_title = match.get('title')
            title_match = re.search(r'(.*) - (.*)', match_title)

            resource_id = int(re.findall(r'd(\d+)', match_id)[0])
            resource_name = title_match.group(1)
            resource_status = title_match.group(2)

            resources[resource_id] = {
                'name': resource_name,
                'state': resource_status
            }

        return resources

    def available_start_time_by_resource_id(self, resource_id):
        resp = self.adapter.get(
            endpoint='MyPC/Front.aspx',
            params={
                'page': 'booking',
                'command': 'add',
                'userId': '',
                'resourceId': resource_id,
                'date': str(datetime.datetime.now().date()),
                'startTime': '00:00',
                'dialogId': 'dialog0'
            }
        )

        soup = BeautifulSoup(resp.text, 'html.parser')
        start_time_select = soup.find('select', attrs={'id': 'startTime'})
        return [option.get('value') for option in start_time_select.find_all('option')]

    def list_bookings(self):
        resp = self.adapter.get(
            endpoint='MyPC/Front.aspx',
            params={
                'page': 'search'
            }
        )

        soup = BeautifulSoup(resp.text, 'html.parser')
        matches = soup.find_all('tr', attrs={'class': ['oddRow', 'evenRow']})

        keys = ['booking_date', 'start_time', 'end_time', 'duration', 'site', 'location', 'resource', 'booking_id']
        bookings = []
        for match in matches:
            cells = match.find_all('td')
            children = [cell.renderContents().strip().decode('utf8') for cell in cells][:-1]
            booking_url = cells[-1].find('a').get('href')
            booking_id = re.search('bookingId=(.*)&', booking_url).group(1)
            children.append(booking_id)

            booking = {}
            for i in range(len(children)):
                booking[keys[i]] = children[i]
            bookings.append(booking)

        return bookings

    def list_bookings_for(self, username, from_date=datetime.date.today().strftime('%d/%m/%Y'),
                          to_date=(datetime.date.today() + datetime.timedelta(days=365)).strftime('%d/%m/%Y')):
        resp = self.adapter.get(
            endpoint='MyPC/Front.aspx',
            params={
                'page': 'search',
                'submitted': 1,
                'bookedForUser': username,
                'bookingType': -1,
                'fromDate': from_date,
                'toDate': to_date
            }
        )

        soup = BeautifulSoup(resp.text, 'html.parser')
        matches = soup.find_all('tr', attrs={'class': ['oddRow', 'evenRow']})

        keys = ['booked_for', 'booking_date', 'start_time', 'end_time', 'duration', 'site', 'location', 'resource',
                'booking_type', 'booking_method', 'booked_by', 'booking_id']
        bookings = []
        for match in matches:
            cells = match.find_all('td')
            children = [cell.renderContents().strip().decode('utf8') for cell in cells][:-1]
            booking_url = cells[-1].find('a').get('href')
            booking_id = re.search('bookingId=(.*)&', booking_url).group(1)
            children.append(booking_id)

            booking = {}
            for i in range(len(children)):
                booking[keys[i]] = children[i]
            bookings.append(booking)

        return bookings

    def delete_booking(self, booking_id, email_receipt):
        resp = self.adapter.post(
            endpoint='MyPC/Front.aspx',
            params={
                'selfBooking': True,
                'page': 'booking',
                'command': 'delete',
                'bookingId': booking_id,  # Integer eg 2570658
                'emailReceipt': email_receipt  # Boolean
            }
        )

        # Get errors if they exist
        soup = BeautifulSoup(resp.text, 'html.parser')
        matches = soup.find('div', attrs={'class': 'expectedException'}) or []
        errors = [match.renderContents().strip().decode('utf8') for match in matches]

        if errors:
            raise Exception('Delete failed. Error: {}'.format(', '.join(errors)))
        if 'javascript:refreshBookingStrip' not in resp.text:
            raise Exception('Unexpected error: {}'.format(resp.text))

        return True

    def create_booking(self, start_time, end_time, booking_date, resource_id, email_receipt):
        resp = self.adapter.post(
            endpoint='MyPC/Front.aspx',
            params={
                'selfBooking': True,
                'startTime': start_time,  # Timestamp eg 00:00:00
                'endTime': end_time,  # Timestamp eg 00:00:00
                'emailReceipt': email_receipt,  # Boolean
                'date': booking_date,  # Date eg 20/08/2016
                'resourceId': resource_id,  # Integer eg 210
                'page': 'booking',
                'command': 'create',
            }
        )

        # Get errors if they exist
        soup = BeautifulSoup(resp.text, 'html.parser')
        matches = soup.find('div', attrs={'class': 'expectedException'}) or []
        errors = [match.strip() for match in matches]

        if errors:
            raise Exception('Booking failed. Error: {}'.format(', '.join(errors)))
        if 'javascript:refreshBookingStrip' not in resp.text:
            raise Exception('Unexpected error: {}'.format(resp.text))

        return True

    def server_status(self):
        resp = self.adapter.get(
            endpoint='MyPC/Front.aspx?page=getResourceStatesAPI'
        )

        return resp.status_code != 200 or not self._to_json(resp.text)

    def _to_json(self, text):
        try:
            return json.loads(text)
        except:
            return None
