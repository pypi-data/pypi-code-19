from bigparser.bigparser import bigparser


class auth:
    authId = None

    def __init__(self):
        self.authId = None
    @classmethod
    def login(self, email, password):
        self.authId = bigparser.login(email, password)
        return self.authId
