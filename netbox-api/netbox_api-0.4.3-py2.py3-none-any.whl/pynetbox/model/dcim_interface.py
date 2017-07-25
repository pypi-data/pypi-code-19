class InterfaceDevice(object):
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


class FormFactor(object):
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


class Connection(object):
    def __init__(self, id=None, url=None, connection_status=None):
        self.id = id
        self.url = url
        self.connection_status = connection_status

    def to_dict(self):
        contents = dict()
        contents['id'] = self.id
        contents['url'] = self.url
        contents['connection_status'] = self.connection_status

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)


class FormFactor(object):
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


class ConnectedInterface(object):
    def __init__(self, device=None, form_factor=None, id=None, url=None, name=None, lag=None, mac_address=None,
                 mgmt_only=None, description=None):
        self.device = InterfaceDevice.from_dict(device)
        self.form_factor = FormFactor.from_dict(form_factor)
        self.id = id
        self.url = url
        self.name = name
        self.lag = lag
        self.mac_address = mac_address
        self.mgmt_only = mgmt_only
        self.description = description

    def to_dict(self):
        contents = dict()
        contents['device'] = self.device.to_dict()
        contents['form_factor'] = self.form_factor.to_dict()
        contents['id'] = self.id
        contents['url'] = self.url
        contents['name'] = self.name
        contents['lag'] = self.lag
        contents['mac_address'] = self.mac_address
        contents['mgmt_only'] = self.mgmt_only
        contents['description'] = self.description

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)


class Interface(object):
    def __init__(self, device=None, form_factor=None, connection=None, connected_interface=None, id=None, name=None,
                 lag=None, mac_address=None, mgmt_only=None, description=None):
        self.device = InterfaceDevice.from_dict(device)
        self.form_factor = FormFactor.from_dict(form_factor)
        self.connection = Connection.from_dict(connection)
        self.connected_interface = ConnectedInterface.from_dict(connected_interface)
        self.id = id
        self.name = name
        self.lag = lag
        self.mac_address = mac_address
        self.mgmt_only = mgmt_only
        self.description = description

    def to_dict(self):
        contents = dict()
        contents['device'] = self.device.to_dict()
        contents['form_factor'] = self.form_factor.to_dict()
        contents['connection'] = self.connection.to_dict()
        contents['connected_interface'] = self.connected_interface.to_dict()
        contents['id'] = self.id
        contents['name'] = self.name
        contents['lag'] = self.lag
        contents['mac_address'] = self.mac_address
        contents['mgmt_only'] = self.mgmt_only
        contents['description'] = self.description

        return contents

    @classmethod
    def from_dict(cls, contents):
        if contents is None:
            return cls()

        return cls(**contents)
