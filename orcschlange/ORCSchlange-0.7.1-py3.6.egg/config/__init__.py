"""Configurations of the program."""
import json
import ORCSchlange.sql


class Config:
    """Main config object as an singleton"""
    class SingeltonObject:
        """Enclosed class that hold the information."""
        def __init__(self, args):
            """Initialization of the class."""
            self.client_id = None
            self.client_secret = None
            self.api = None
            self.auth = None
            self.ready = False
            if args.config == 0:
                self.sandbox()
                self.ready = True
            elif args.config == 1:
                if self.read_db(args.dbfile):
                    self.ready = True
            elif isinstance(args.config, str):
                if self.read_file(args.config):
                    self.ready = True
            else:
                self.read_inline(*args.config)
                self.ready = True

        def sandbox(self):
            """Connect with the ORCID sandbox."""
            self.client_id = "APP-DZ4II2NELOUB89VC"
            self.client_secret = "c0a5796e-4ed3-494b-987e-827755174718"

            self.api = "https://pub.sandbox.orcid.org/v2.0"
            self.auth = "https://sandbox.orcid.org/oauth/token"

        def read_db(self, path):
            """Read connection information from the db"""
            db = ORCSchlange.sql.DB(path)
            conf = db.read_config()
            db.close()
            if conf is None:
                return False
            self.api = conf[0]
            self.auth = conf[1]
            self.client_id = conf[2]
            self.client_secret = conf[3]
            return True

        def read_file(self, path):
            """Read connection information from a file"""
            try:
                f = open(path)
                content = f.read()
                f.close()
                js = json.loads(content)
                self.client_id = js["client_id"]
                self.client_secret = js["client_secret"]
                self.auth = js["auth"] if "auth" in js else "https://orcid.org/oauth/token"
                self.api = js["api"] if "api" in js else "https://pub.orcid.org/v2.0/"
                return True
            except:
                return False

        def read_inline(self, clientid, secret):
            """Read connection information from the args."""
            self.client_id = clientid
            self.client_secret = secret
            self.api = "https://orcid.org/oauth/token"
            self.auth = "https://pub.orcid.org/v2.0/"

        def __str__(self):
            """Make a string representation of the config."""
            return "{0} - {1}\n{2}\n{3}".format(self.client_id, self.client_secret, self.auth, self.api)

    instance = None

    def __init__(self, args=None):
        """Initialize the outer class if not already done initialize the inner class."""
        if not Config.instance:
            if args:
                Config.instance = Config.SingeltonObject(args)

    def __getattr__(self, name):
        """Get attributes from the inner class."""
        return getattr(self.instance, name)

    def __str__(self):
        """Represent the outer class with the inner class."""
        return str(self.instance)
