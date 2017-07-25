from netbox_api.model.common import CustomFields


class Manufacturer(object):
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


class DeviceType(object):
    def __init__(self, manufacturer=None, id=None, url=None, model=None, slug=None):
        self.manufacturer = Manufacturer.from_dict(manufacturer)
        self.id = id
        self.url = url
        self.model = model
        self.slug = slug

    def to_dict(self):
        contents = dict()
        contents['manufacturer'] = self.manufacturer.to_dict()
        contents['id'] = self.id
        contents['url'] = self.url
        contents['model'] = self.model
        contents['slug'] = self.slug

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)


class DeviceRole(object):
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


class Tenant(object):
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


class Platform(object):
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


class DeviceSite(object):
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


class Rack(object):
    def __init__(self, id=None, url=None, name=None, display_name=None):
        self.id = id
        self.url = url
        self.name = name
        self.display_name = display_name

    def to_dict(self):
        contents = dict()
        contents['id'] = self.id
        contents['url'] = self.url
        contents['name'] = self.name
        contents['display_name'] = self.display_name

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)


class Face(object):
    def __init__(self, value=None, label=None):
        self.value = value
        self.label = label

    def to_dict(self):
        contents = dict()
        contents['value'] = self.value
        contents['label'] = self.label

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)


class Status(object):
    def __init__(self, value=None, label=None):
        self.value = value
        self.label = label

    def to_dict(self):
        contents = dict()
        contents['value'] = self.value
        contents['label'] = self.label

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)


class PrimaryIp(object):
    def __init__(self, id=None, url=None, family=None, address=None):
        self.id = id
        self.url = url
        self.family = family
        self.address = address

    def to_dict(self):
        contents = dict()
        contents['id'] = self.id
        contents['url'] = self.url
        contents['family'] = self.family
        contents['address'] = self.address

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)


class PrimaryIp4(object):
    def __init__(self, id=None, url=None, family=None, address=None):
        self.id = id
        self.url = url
        self.family = family
        self.address = address

    def to_dict(self):
        contents = dict()
        contents['id'] = self.id
        contents['url'] = self.url
        contents['family'] = self.family
        contents['address'] = self.address

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)


class Device(object):
    def __init__(self, device_type=None, device_role=None, tenant=None, platform=None, site=None, rack=None, face=None,
                 status=None, primary_ip=None, primary_ip4=None, custom_fields=None, id=None, name=None,
                 display_name=None, serial=None, asset_tag=None, position=None, parent_device=None, primary_ip6=None,
                 comments=None):
        self.device_type = DeviceType.from_dict(device_type)
        self.device_role = DeviceRole.from_dict(device_role)
        self.tenant = Tenant.from_dict(tenant)
        self.platform = Platform.from_dict(platform)
        self.site = DeviceSite.from_dict(site)
        self.rack = Rack.from_dict(rack)
        self.face = Face.from_dict(face)
        self.status = Status.from_dict(status)
        self.primary_ip = PrimaryIp.from_dict(primary_ip)
        self.primary_ip4 = PrimaryIp4.from_dict(primary_ip4)
        self.custom_fields = CustomFields.from_dict(custom_fields)
        self.id = id
        self.name = name
        self.display_name = display_name
        self.serial = serial
        self.asset_tag = asset_tag
        self.position = position
        self.parent_device = parent_device
        self.primary_ip6 = primary_ip6
        self.comments = comments

    def to_dict(self):
        contents = dict()
        contents['device_type'] = self.device_type.to_dict()
        contents['device_role'] = self.device_role.to_dict()
        contents['tenant'] = self.tenant.to_dict()
        contents['platform'] = self.platform.to_dict()
        contents['site'] = self.site.to_dict()
        contents['rack'] = self.rack.to_dict()
        contents['face'] = self.face.to_dict()
        contents['status'] = self.status.to_dict()
        contents['primary_ip'] = self.primary_ip.to_dict()
        contents['primary_ip4'] = self.primary_ip4.to_dict()
        contents['custom_fields'] = self.custom_fields.to_dict()
        contents['id'] = self.id
        contents['name'] = self.name
        contents['display_name'] = self.display_name
        contents['serial'] = self.serial
        contents['asset_tag'] = self.asset_tag
        contents['position'] = self.position
        contents['parent_device'] = self.parent_device
        contents['primary_ip6'] = self.primary_ip6
        contents['comments'] = self.comments

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)
