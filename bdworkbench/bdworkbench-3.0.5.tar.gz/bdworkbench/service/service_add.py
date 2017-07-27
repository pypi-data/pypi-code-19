#
# Copyright (c) 2016 BlueData Software, Inc.
#
from __future__ import print_function
from .. import SubCommand
from ..constants import *
from ..inmem_store import ENTRY_DICT

class ServiceAdd(SubCommand):
    """

    """

    def __init__(self, config, inmemStore, cmdObj):
        SubCommand.__init__(self, config, inmemStore, cmdObj, 'add')

    def getSubcmdDescripton(self):
        return 'Add a new service to the catalog entry.'

    def populateParserArgs(self, subparser):
        subparser.add_argument('--srvcid', metavar='SERVICE_ID', type=str,
                               required=True, dest='srvcid',
                               help='A catalog entry wide unique service id.')
        subparser.add_argument('-n', '--name', dest='name', type=str,
                               action='store', required=True,
                               help='Service name to be displayed.')
        subparser.add_argument('--export_as', metavar='EXPORTED_NAME', dest='export', type=str,
                                action='store',
                                help='The name this service is exported as in the bluedata UI')
        subparser.add_argument('-s', '--scheme', dest='scheme', type=str,
                               action='store', default=None,
                               help='URI scheme for the service, if any.')
        subparser.add_argument('--port', dest='port', type=int, action='store',
                               default=None,
                               help='URI port number, if any.')
        subparser.add_argument('--path', dest='path', type=str, action='store',
                               default=None,
                               help='URI path for the service, if any.')
        subparser.add_argument('--display', dest='isdash', action='store_true',
                               default=DEFAULT_BOOL_FALSE,
                               help='Display the service to the end user on the '
                                    'cluster details page.')

    def run(self, pArgs):
        existing = self._get_existing_srvc(pArgs.srvcid)
        if existing == None:
            valueDict = {}
            self._update_srvc_dict(valueDict, pArgs)
            self.inmemStore.appendValue(ENTRY_DICT, "services", valueDict)
        else:
            self._update_srvc_dict(existing, pArgs)

        return True

    def _update_srvc_dict(self, valueDict, pArgs):
        """

        """
        valueDict['id'] = pArgs.srvcid
        valueDict['label'] = {"name": pArgs.name}
        valueDict['endpoint'] = { "is_dashboard" : pArgs.isdash }
        if pArgs.export != None:
            valueDict["exported_service"] = pArgs.export

        if pArgs.scheme != None:
            valueDict["endpoint"]["url_scheme"] = pArgs.scheme

        if pArgs.port != None:
            valueDict["endpoint"]["port"] = str(pArgs.port)

        if pArgs.path != None:
            valueDict["endpoint"]["path"] = pArgs.path

    def _get_existing_srvc(self, srvcId):
        """

        """
        entryDict = self.inmemStore.getDict(ENTRY_DICT)
        try:
            services = entryDict["services"]

            for srvc in services:
                if srvc['id'] == srvcId:
                    return srvc
        except Exception as e:
            pass

        return None


    def complete(self, text, argsList):
        return []
