import psycopg2cffi as psycopg2

IFACE_TYPES = {
    'rj45': 1000,
    'sfp': 1100,
    'sfp+': 1200,
    'qsfp+': 1400,
    'other': 32767
}


class EntityNotFoundException(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg


class DeviceInterface(object):
    def __init__(self, db_id, name, form_factor, mgmt_only, mac_address):
        self.id = db_id
        self.name = name
        self.form_factor = form_factor
        self.mgmt_only = mgmt_only
        self.mac_address = mac_address

    def __str__(self):
        return self.name


class Device(object):
    def __init__(self, db_id, name, tags=None):
        self.id = db_id
        self.name = name
        self.tags = tags if tags is not None else list()
        self.interfaces = list()

    def __str__(self):
        return self.name


class NetboxDBClient(object):
    def __init__(self, user, password, db_name='netbox', db_host='localhost'):
        self._user = user
        self._password = password
        self._db_name = db_name
        self._db_host = db_host

        # Client caching of info and connection management
        self._loaded = False
        self._connection = None

        # Values for custom fields - in this case, tags
        self._tags_field_id = None
        self._tags_obj_type_id = None

    def _load(self, conn):
        cursor = conn.cursor()

        try:
            cursor.execute('select id from extras_customfield where name = %s;', ('Tags',))
            self._tags_field_id = cursor.fetchone()[0]

            cursor.execute('select contenttype_id from extras_customfield_obj_type where customfield_id = %s;',
                           (self._tags_field_id,))
            self._tags_obj_type_id = cursor.fetchone()[0]
        finally:
            cursor.close()

    def close(self):
        if self._connection is not None:
            self._connection.close()
            self._connection = None

    def _commit(self):
        if self._connection is not None:
            self._connection.commit()

    def _open(self):
        self._connection = psycopg2.connect("dbname='{}' host='{}' user='{}' password='{}'".format(
            self._db_name,
            self._db_host,
            self._user,
            self._password))

        if self._loaded is False:
            self._load(self._connection)

        return self._connection

    def _cursor(self):
        if self._connection is None:
            self._open()

        return self._connection.cursor()

    def device(self, name):
        cursor = self._cursor()

        try:
            cursor.execute('select id, name from dcim_device where name = %s;', (name,))

            if cursor.rowcount == 0:
                raise EntityNotFoundException('Device {} not found.'.format(name))

            row = cursor.fetchone()
            return Device(row[0], row[1])
        finally:
            cursor.close()

    def device_id(self, device_name):
        cursor = self._cursor()

        try:
            cursor.execute('select id from dcim_device where name = %s;', (device_name,))

            if cursor.rowcount == 0:
                raise EntityNotFoundException('Device {} not found.'.format(device_name))

            return cursor.fetchone()[0]
        finally:
            cursor.close()

    def all_devices(self):
        devices = list()
        cursor = self._cursor()

        try:
            cursor.execute('select id, name from dcim_device;')

            for row in cursor:
                device_id = row[0]
                device_name = row[1]
                device_tags = self.device_tags(device_id=device_id)

                devices.append(Device(device_id, device_name, device_tags))

            return devices
        finally:
            cursor.close()

    def create_ipaddress(self, address, family=4, interface_id=None, tenant_id=1, status=1, description=''):
        cursor = self._cursor()
        try:
            cursor.execute(
                'insert into ipam_ipaddress (created, last_updated, description, family, address, interface_id, tenant_id, status) values (%s, %s, %s, %s, %s, %s, %s, %s)',
                ('now()', 'now()', description, family, address, interface_id, tenant_id, status,))

            self._commit()
        finally:
            cursor.close()

    def ipaddress_id(self, address):
        cursor = self._cursor()
        try:
            cursor.execute('select id from ipam_ipaddress where address = %s',
                           (address,))

            if cursor.rowcount == 0:
                return None

            return cursor.fetchone()[0]
        finally:
            cursor.close()

    def assign_ipaddress(self, device, interface, address):
        address_id = self.ipaddress_id(address)
        if address_id is None:
            self.create_ipaddress(address)
            address_id = self.ipaddress_id(address)

        device_interfaces = self.device_interfaces(device)

        target_iface = None
        for iface in device_interfaces:
            if iface.name == interface:
                target_iface = iface
                break

        if target_iface is None:
            raise Exception('Unable to find interface {} on device {}'.format(interface, device))

        cursor = self._cursor()
        try:
            cursor.execute(
                'update ipam_ipaddress set interface_id = %s where id = %s',
                (target_iface.id, address_id,))

            self._commit()
        finally:
            cursor.close()

    def add_interface(self, device_name, iface_name, form_factor, mgmt_only, mac_address=None, description=''):
        # Get the device first
        device = self.device(device_name)
        cursor = self._cursor()

        try:
            if mac_address is None:
                cursor.execute(
                    'insert into dcim_interface (name, form_factor, mgmt_only, device_id, description) values (%s, %s, %s, %s, %s)',
                    (iface_name, form_factor, mgmt_only, device.id, description))
            else:
                cursor.execute(
                    'insert into dcim_interface (name, form_factor, mgmt_only, mac_address, device_id, description) values (%s, %s, %s, %s, %s, %s)',
                    (iface_name, form_factor, mgmt_only, mac_address, device.id, description))
            self._commit()
        finally:
            cursor.close()

    def delete_interfaces(self, name):
        # Get the device first
        device = self.device(name)
        cursor = self._cursor()

        try:
            # Unbind IP Addresses
            cursor.execute(
                'update ipam_ipaddress set interface_id=NULL where interface_id in (select id from dcim_interface where device_id = %s)',
                (device.id,))

            # Remove the interfaces
            cursor.execute(
                'delete from dcim_interface where device_id = %s',
                (device.id,))

            self._commit()
        finally:
            cursor.close()

    def update_interface(self, interface):
        cursor = self._cursor()
        try:
            cursor.execute(
                'update dcim_interface set name=%s,form_factor=%s,mgmt_only=%s,mac_address=%s where id = %s',
                (interface.name, interface.form_factor, interface.mgmt_only, interface.mac_address, interface.id,))

            self._commit()
        finally:
            cursor.close()

    def device_interfaces(self, name):
        # Get the device first
        device = self.device(name)

        # Look up interfaces next
        cursor = self._cursor()
        try:
            cursor.execute(
                'select id, name, form_factor, mgmt_only, mac_address from dcim_interface where device_id = %s',
                (device.id,))

            interfaces = list()
            for row in cursor:
                interfaces.append(DeviceInterface(
                    db_id=row[0],
                    name=row[1],
                    form_factor=row[2],
                    mgmt_only=row[3],
                    mac_address=row[4]))

            return interfaces
        finally:
            cursor.close()

    def device_tags(self, device_name=None, device_id=None):
        cursor = self._cursor()

        try:
            if device_id is None:
                device_id = self.device_id(device_name)

            cursor.execute(
                'select serialized_value from extras_customfieldvalue where obj_id = %s and field_id = %s',
                (device_id, self._tags_field_id))

            if cursor.rowcount == 1:
                tags_str = cursor.fetchone()[0]
                return tags_str.split(',')
            else:
                return None
        finally:
            cursor.close()

    def set_device_tags(self, device_name, tags):
        formatted_tags = ','.join(tags)

        cursor = self._cursor()

        try:
            device_id = self.device_id(device_name)

            if self.device_tags(device_name, device_id) is None:
                cursor.execute(
                    'insert into extras_customfieldvalue (obj_id, serialized_value, field_id, obj_type_id) values (%s, %s, %s, %s)',
                    (device_id, formatted_tags, self._tags_field_id, self._tags_obj_type_id))
            else:
                cursor.execute(
                    'update extras_customfieldvalue set serialized_value = %s where obj_id = %s and field_id = %s',
                    (formatted_tags, device_id, self._tags_field_id))

            self._commit()
        finally:
            cursor.close()
