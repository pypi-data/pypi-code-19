from AwsProcessor import AwsProcessor
from stdplusAwsHelpers.AwsConnectionFactory import AwsConnectionFactory
from CommandArgumentParser import CommandArgumentParser

from pprint import pprint

class AwsLogStream(AwsProcessor):
    def __init__(self,logStream,parent):
        """Construct an AwsLogStream command processor"""
        AwsProcessor.__init__(self,parent.raw_prompt + "/logStream:" + logStream['logStreamName'],parent)
        self.stackResource = None
        self.logStream = logStream
        self.do_tail([])

    def do_tail(self,args):
        """Tail the logs"""
        response = AwsConnectionFactory.getLogClient().get_log_events(
                logGroupName=self.logStream['logGroupName'],
                logStreamName=self.logStream['logStreamName'],
                limit=10,
                startFromHead=False
            )
        pprint(response)
