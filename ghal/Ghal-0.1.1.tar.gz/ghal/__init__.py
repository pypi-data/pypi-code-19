""" Githost Abstraction Layer """


def hello():
    """ Greet """
    return True


class GithostConnection(object):  # pylint: disable=too-few-public-methods
    """ Establish a connection """
    healthy = True


def connect(_, __):
    """ Establish a connection """
    return GithostConnection()
