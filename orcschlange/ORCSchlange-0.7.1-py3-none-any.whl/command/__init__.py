"""Package that contains the base commands of the program."""
import logging
from ORCSchlange.sql import DB


def really(question):
    """Ask a Yes/Mo question at the prompt.
    
    :param question: The question that is asked.
    :return: True if the response starts with a y.
    """
    ask = ""
    while not ask.startswith("y") and not ask.startswith("n"):
        ask = input(question).lower()
    return ask.startswith("y")


class BaseCommand:
    """The base Command that initialize the logger and save the arguments."""
    
    logger = None
    
    def __init__(self, args):
        """Save the arguments and initialize the logger.
        
        Save the arguments in args. Also if not happen initialize the logger.
        If the verbose flag is not set overwrite debug function with an empty function.
        
        :param args: The argument i.e. the given command line parameters.
        """
        self.args = args
        self.db = None
        if self.logger is None:
            self.logger = logging.Logger(name="logging loui")
            self.logger.setLevel(logging.DEBUG)
            ch = logging.StreamHandler()
            ch.setLevel(logging.DEBUG)
            formatter = logging.Formatter("%(levelname)-5s %(asctime)s: %(message)s", "%H:%M:%S")
            ch.setFormatter(formatter)
            self.logger.addHandler(ch)
        if not self.args.verbose:
            self.debug = lambda x: None
    
    def debug(self, ret):
        """ Make an debug output.
        
        :param ret: The text that is reported as info.
        """
        self.logger.info(ret)
    
    def error(self, ret):
        """Make an error output.
        
        :param ret: The text that is reported as error.
        """
        self.logger.error(ret)
    
    def open(self):
        """Open an SQLite DB connection."""
        if self.db is None:
            self.debug("Open db file {0}".format(self.args.dbfile))
            self.db = DB(self.args.dbfile)
        else:
            self.error("DB connection is already open.")
    
    def close(self):
        """Close the SQLite DB connection."""
        if self.db is not None:
            self.debug("Close db file {0}".format(self.args.dbfile))
            self.db.close()
            self.db = None
        else:
            self.error("DB connection is already closed.")
