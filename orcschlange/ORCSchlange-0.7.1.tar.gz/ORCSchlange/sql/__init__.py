"""Package that handle the SQLite db that runs in the background."""
from sqlite3 import connect, OperationalError, IntegrityError
from ORCSchlange.orcid import OrcID


class DB:
    """The class that interact with the SQLite db."""
    def __init__(self, path="output/people.db"):
        """Initialize the connection with the file where the db is saved.
        
        If the file not already exists it is created with an empty db in it.
        
        :param path: The path to the file that contains the SQLite db.
        """
        self.conn = connect(path)
        self.c = self.conn.cursor()

    def __get_list(self):
        """Get all orcid entries.
        
        :return: A list of orcids as tuples.
        """
        self.c.execute('SELECT * FROM people')
        return self.c.fetchall()

    def get_orcids(self):
        """Get all orcid entries as OrcID object.
        
        :return: An iterator over all orcids in the db as OrcID object.
        """
        return (OrcID(*t) for t in self.__get_list())

    def close(self):
        """Close the connection to the SQLite db."""
        self.conn.close()

    def create_db(self):
        """Create a new SQLite db.
        
        The file is created by the connection these function only create the table that holds the orcids.
        It is necessary to call these function once before adding operations are possible.
        
        :return: True if the db is created. Falls if it already exists.
        """
        try:
            self.c.execute("CREATE TABLE people (orcid CHARACTER(16) PRIMARY KEY, start DATE, end DATE)")
            self.conn.commit()
            return True
        except OperationalError:
            return False

    def drop_db(self):
        """Drop the SQLite db.
        
        The file is not delete by these function, it only drop the table that holds the orcids.
        It create no error if the table not exists.
        These make it  save to call these function before a create_db independent if the table really exists before.
        """
        try:
            self.c.execute("DROP TABLE people")
            self.conn.commit()
        except OperationalError:
            pass

    def add_user(self, orcid, start, stop):
        """Add a new user to the db.
        
        :param orcid: The id of the member.
        :param start: The start of the time in which the paper are fetched.
        :param stop:  The end of the time in which the paper are fetched.
        :return: 0 if the user is added. 1 if a doubled entry is found and 2 if no db exists to insert.
        """
        try:
            self.c.execute("INSERT INTO people VALUES (?,?,?)", (orcid, start, stop))
            self.conn.commit()
            return 0
        except IntegrityError:
            return 1
        except OperationalError:
            return 2

    def create_test_db(self):
        """Create a test db with three sandbox ids."""
        self.drop_db()
        self.create_db()
        self.add_user("0000000219094153", "1900-01-01", "2016-12-31")
        self.add_user("000000020183570X", "1900-01-01", "2016-12-31")
        self.add_user("0000000303977442", "1900-01-01", None)

    def add_config(self, client_id, secret, auth, api):
        """Add config data to the db.
        
        It adds the config in a special table that is cleand before new data is insert.
        So that exactly one entry exists. If old dater exists before they are discarded.
        Also a clean or drop command have no influence on these table.
        
        :param client_id: The client id of you app.
        :param secret: The client secret of you app.
        :param auth: The url to authenticate.
        :param api: The url of the api.
        """
        try:
            self.c.execute("DROP TABLE config")
            self.conn.commit()
        except OperationalError:
            pass
        self.c.execute("CREATE TABLE config (api TEXT, auth TEXT, id TEXT, secret TEXT)")
        self.conn.commit()
        self.c.execute("INSERT INTO config VALUES (?,?,?,?)", (api, auth, client_id, secret))
        self.conn.commit()

    def read_config(self):
        """Read the config data from the db
        
        :return: The data as a tuple.
        """
        try:
            self.c.execute('SELECT * FROM config')
        except OperationalError:
            return None
        return self.c.fetchone()
