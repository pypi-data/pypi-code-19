from stuffer.core import Action


class AddToGroup(Action):
    """Add a user to a group."""

    def __init__(self, user, group):
        super().__init__()
        self.user = user
        self.group = group

    def command(self):
        return "adduser {} {}".format(self.user, self.group)

