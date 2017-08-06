import os 

class Workspace:

    home = os.path.expanduser("~")
    data = os.path.join(home, "data")
    if not os.path.exists(data):
        data = home
    database = os.path.join(data, "database")
    image = os.path.join(data, "image")

    def __init__(self, home=None):
        if home is None:
            home = self.__class__.home
        self.home = home
        self.data = os.path.join(self.home, "data")
        if not os.path.exists(self.data):
            self.data = self.home            
        self.database = os.path.join(self.data, "database")
        self.image = os.path.join(self.data, "image")
        self.workspace = self.data

    def __call__(self, *args):
        path = os.path.join(self.workspace, *args)
        return path

    




