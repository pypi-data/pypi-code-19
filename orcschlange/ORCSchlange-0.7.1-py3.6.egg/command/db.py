"""The db commands."""
import sys
from ORCSchlange.command import BaseCommand, really


def check_date(d):
    """Check if a string is a valide date of the form "YYYY-MM-DD".
    
    :param d: The date string that is checked.
    :return: True if it is a not valid date string.
    """
    if len(d) != 10:
        return True
    split = d.split("-")
    return len(split) != 3 or not split[0].isdecimal() or not split[1].isdecimal() or not split[2].isdecimal()


class DbCommand(BaseCommand):
    """The class that contains all db commands."""
    
    def add(self):
        """Add an new orcid to the db."""
        self.open()
        self.debug("Validate orchid")
        self.args.orchid = self.args.orchid.replace("-", "")
        if len(self.args.orchid) != 16:
            self.error("Invalide orchid")
            self.close()
            sys.exit(1)
        self.debug("Validate start")
        if check_date(self.args.start):
            self.error("Invalide start")
            self.close()
            sys.exit(1)
        if self.args.stop:
            self.debug("Stop found")
            self.debug("Validate stop")
            if check_date(self.args.stop):
                self.error("Invalide stop")
                sys.exit(1)
            self.debug("Add orcid")
            add_code = self.db.add_user(self.args.orchid, self.args.start, self.args.stop)
            if add_code == 1:
                self.error("Doubled orchid entry. Nothing have been added.")
            elif add_code == 2:
                self.error("No db found. Try to use \"db create\" command first.")
        else:
            self.debug("Add orcid")
            add_code = self.db.add_user(self.args.orchid, self.args.start, None)
            if add_code == 1:
                self.error("Doubled orchid entry. Nothing have been added.")
            elif add_code == 2:
                self.error("No db found. Try to use \"db create\" command first.")
        self.close()
    
    def prints(self):
        """Prints all orcids that are in the db."""
        self.open()
        for orc in self.db.get_orcids():
            print(orc)
        self.close()
    
    def clean(self):
        """Clean the db i.e. delet all orcids in the db.
        
        It is ask if the db realy should be dropped. If the answer is yes al entries are deleted.
        """
        question = "Do you really want to delete the complete db? (Y/N)\n"
        if really(question):
            self.open()
            self.debug("Drop old DB")
            self.db.drop_db()
            self.debug("Create new DB")
            self.db.create_db()
            self.close()
    
    def create(self):
        """Create an empty db. It is necessary before any add function."""
        self.open()
        self.debug("Create new DB")
        if not self.db.create_db():
            self.error("DB already exists")
        self.close()
    
    def create_test(self):
        """Drop old db and create the test DB with three entries."""
        question = "Do you really want to delete the complete db and create a db with test entries? (Y/N)\n"
        if really(question):
            self.open()
            self.debug("Create test DB")
            self.db.create_test_db()
            self.close()
    
    def add_conf(self):
        """Insert an config information and overwrite old entry."""
        self.open()
        self.debug("Insert config in DB")
        self.db.add_config(self.args.cliend_id, self.args.clien_secret, self.args.auth, self.args.api)
        self.close()
