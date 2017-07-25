from netbox_api.model.common import CustomFields


class SiteTenant(object):
    def __init__(self, id=None, url=None, name=None, slug=None):
        self.id = id
        self.url = url
        self.name = name
        self.slug = slug

    def to_dict(self):
        contents = dict()
        contents['id'] = self.id
        contents['url'] = self.url
        contents['name'] = self.name
        contents['slug'] = self.slug

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)


class Site(object):
    def __init__(self, tenant=None, custom_fields=None, id=None, name=None, slug=None, region=None, facility=None,
                 asn=None, physical_address=None, shipping_address=None, contact_name=None, contact_phone=None,
                 contact_email=None, comments=None, count_prefixes=None, count_vlans=None, count_racks=None,
                 count_devices=None, count_circuits=None):
        self.tenant = SiteTenant.from_dict(tenant)
        self.custom_fields = CustomFields.from_dict(custom_fields)
        self.id = id
        self.name = name
        self.slug = slug
        self.region = region
        self.facility = facility
        self.asn = asn
        self.physical_address = physical_address
        self.shipping_address = shipping_address
        self.contact_name = contact_name
        self.contact_phone = contact_phone
        self.contact_email = contact_email
        self.comments = comments
        self.count_prefixes = count_prefixes
        self.count_vlans = count_vlans
        self.count_racks = count_racks
        self.count_devices = count_devices
        self.count_circuits = count_circuits

    def to_dict(self):
        contents = dict()
        contents['tenant'] = self.tenant.to_dict()
        contents['custom_fields'] = self.custom_fields.to_dict()
        contents['id'] = self.id
        contents['name'] = self.name
        contents['slug'] = self.slug
        contents['region'] = self.region
        contents['facility'] = self.facility
        contents['asn'] = self.asn
        contents['physical_address'] = self.physical_address
        contents['shipping_address'] = self.shipping_address
        contents['contact_name'] = self.contact_name
        contents['contact_phone'] = self.contact_phone
        contents['contact_email'] = self.contact_email
        contents['comments'] = self.comments
        contents['count_prefixes'] = self.count_prefixes
        contents['count_vlans'] = self.count_vlans
        contents['count_racks'] = self.count_racks
        contents['count_devices'] = self.count_devices
        contents['count_circuits'] = self.count_circuits

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)
