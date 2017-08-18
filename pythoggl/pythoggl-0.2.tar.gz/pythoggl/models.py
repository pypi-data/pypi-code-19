import json

class Workspace:
    """
        class that models the Workspace object
    """

    def __init__(self, response):
        for key in response:
            setattr(self, key, response[key])

class Project:
    """
        class that models the Project object
    """

    def __init__(self, response):
        for key in response:
            setattr(self, key, response[key])
