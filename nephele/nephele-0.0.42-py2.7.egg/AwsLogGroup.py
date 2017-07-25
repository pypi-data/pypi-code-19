import AwsLogStream

from AwsProcessor import AwsProcessor
from stdplusAwsHelpers.AwsConnectionFactory import AwsConnectionFactory
from CommandArgumentParser import CommandArgumentParser

from pprint import pprint

class AwsLogGroup(AwsProcessor):
    def __init__(self,stackResource,parent):
        """Construct an AwsLogGroup command processor"""
        AwsProcessor.__init__(self,parent.raw_prompt + "/logGroup:" + stackResource.logical_id,parent)
        self.stackResource = stackResource
        self.logStreamNamePrefix = None
        self.orderBy = 'LogStreamName'
        self.descending = False
        self.do_refresh('')

    def do_refresh(self,args):
        """Refresh the view of the log group"""
        # prints all the groups: pprint(AwsConnectionFactory.getLogClient().describe_log_groups())

        response = AwsConnectionFactory.getLogClient().describe_log_groups(logGroupNamePrefix=self.stackResource.physical_resource_id)
        if not 'logGroups' in response:
            raise Exception("Expected log group description to have logGroups entry. Got {}".format(response))

        # pprint(response)
        descriptions = [x for x in response['logGroups'] if x['logGroupName'] == self.stackResource.physical_resource_id]
        if not descriptions:
            raise Exception("Could not find log group {} in list {}".format(self.stackResource.physical_resource_id,response['logGroups']))

        self.description = descriptions[0]

        self.logStreams = self.loadLogStreams()
        print "== logStream"
        maxIndex = "{}".format(len(self.logStreams)+1)
        print "maxIndex:{}".format(maxIndex)
        frm = "  {{0:{}d}}: {{1}}".format(len(maxIndex))
        print frm

        index = 0
        for logStream in self.logStreams:
            print frm.format(index,logStream['logStreamName'])
            index += 1

    def loadLogStreams(self):
        response = AwsConnectionFactory.getLogClient().describe_log_streams(logGroupName=self.stackResource.physical_resource_id,
                                                                                           #logStreamNamePrefix=self.logStreamNamePrefix,
                                                                                           orderBy=self.orderBy,
                                                                                           descending=self.descending)
        
        logStreams = response['logStreams']
        for logStream in logStreams:
            logStream['logGroupName']=self.stackResource.physical_resource_id
            
        return logStreams

    def do_logStream(self,args):
        """Go to the specified log stream. logStream -h for detailed help"""
        parser = CommandArgumentParser("logStream")
        parser.add_argument(dest='logStream',help='logStream index.');
        args = vars(parser.parse_args(args))

        print "loading log stream {}".format(args['logStream'])
        index = int(args['logStream'])
        logStream = self.logStreams[index]

        print "logStream:{}".format(logStream)
        self.childLoop(AwsLogStream.AwsLogStream(logStream,self))
        #self.stackResource(logStream.stack_name,logStream.logical_id)
        
