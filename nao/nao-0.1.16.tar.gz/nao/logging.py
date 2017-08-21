

import logging
import datetime

from sqlalchemy import *

class DBHandler(logging.Handler):
    """
    allows the logging into an SqlAlchemy ORM
    
    Uses an engine and sets up separate threadsafe
    connection to that engine
    """

    def __init__(self, engine):
        """

        """
        super().__init__()

        # create table if needed

        # initialize session
        self.session = None

    def formatDBTime(self, record):

        # WARNING modifies created
        record.created = datetime.datetime.fromtimestamp(record.created)


    def emit(self, record):

        # Use default formatting
        self.format(record)

        exc_formatter = logging._defaultFormatter.formatException

        record.exc_text = exc_formatter(record.exc_info) if record.exc_info else ''

        self.session.add(LogRecord(**record.__dict__))
        self.session.commit()

    


class LogRecord(Base):

    inserted =      Column(String, default=datetime.datetime.now)
    created =       Column(Datetime)
    name =          Column(String)
    level =         Column(String)
    module =        Column(String)
    func_name =     Column(String)
    line_no =       Column(String)
    thread =        Column(String)
    thread_name =   Column(String)
    process =       Column(String)
    message =       Column(Text)
    args =          Column(Text)
    exception =     Column(Text)
    

    def parse_message():
        """
        some logic to parse message into YAML and then
        annotate it in the viewer...
        """