"""Defines a class for storing a person's slack profile information."""


class SlackPerson(object):
    """Class for storing/getting slack profile information."""
    def __init__(self, username, team_user_list):
        """Initializes SlackPerson.

        Arguments:
        username: the handle with or without @ used to mention someone
        team_user_list: json object returned by the slack api `users.list`
        method.
        """
        if username[0] == '@':
            username = username[1:]
        self.username = username
        try:
            for user in team_user_list['members']:
                if self.username == user['name']:
                    # parse the json to get the user's info
                    self.userid = user['id']
                    self.email = user['profile']['email']
                    self.fname = user['profile']['first_name']
                    self.lname = user['profile']['last_name']
                    self.team = user['profile']['team']
        except (KeyError, TypeError) as err:
            raise SlackDataError(
                "team_user_list is not formed correctly: {}".format(err))

        # raise an error if the user was not found
        if not hasattr(self, 'userid'):
            raise SlackDataError("{} was not found in the user list".format(
                self.username))

    def __repr__(self):
        """Representation of SlackPerson. This cannot create a SlackPerson
        object.
        """
        return 'SlackPerson(userid={id}, username={name})'.format(
            name=self.username, id=self.userid)


class SlackDataError(Exception):
    """Exception raised if input data is invalid in some way."""
    pass
