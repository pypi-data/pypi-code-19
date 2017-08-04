from .resource import ResourceList, ResourceItem


class UserResourceItem(ResourceItem):
    def __init__(self, id):
        super().__init__('users', id)

    @property
    def username(self):
        return self.data['username']

    @property
    def email(self):
        return self.data['email']

    @property
    def first_name(self):
        return self.data['first_name']

    @property
    def last_name(self):
        return self.data['last_name']

    @classmethod
    def from_auth(cls):
        return UserResourceItem(cls.api.user['id'])

class UserResourceList(ResourceList):
    ITEM = UserResourceItem

    def __init__(self):
        super().__init__('users')
