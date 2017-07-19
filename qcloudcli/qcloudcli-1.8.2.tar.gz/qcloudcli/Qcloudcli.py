#!/usr/bin/env python
# -*- coding: utf-8 -*-

import handleParameter
import handleData
import handleCmd
import result
import showHelp
import autoComplete
import sys
reload(sys)
sys.setdefaultencoding('utf8')

def main():
    handle = QcloudCLI()
    handle.main()

class QcloudCLI:
    def __init__(self):
        self.user_input = sys.argv[1:]
        self.handleParameter = handleParameter.handleParameter()
        self.handleCmd = handleCmd.handleCmd()
        self.handleData = handleData.handleData()
        self.showHelp = showHelp.showHelp()
        self.completer = autoComplete.Completer()

    def main(self):
        module = ''
        #get module such as cvm cdb..maybe extra cmd such as help,version
        if self.user_input.__len__() > 0:
            module = self.user_input[0].lower()

        #show qcloudcli help
        help_cmd = ['help','-h','--help']
        if not module or module.lower() in help_cmd:
            self.handleCmd.showQcloudCliHelp()
            return

        #show version
        version_cmd = ['version','--version']
        if module.lower() in version_cmd:
            self.handleCmd.showVersion()
            return

        #configure qcloudcli
        configure_cmd = ['configure']
        if module.lower() in configure_cmd:
            self.handleCmd.configureQcloudcli()
            return

        #showconfigure qcloudcli
        showconfigure_cmd = ['showconfigure']
        if module.lower() in showconfigure_cmd:
            self.handleCmd.showconfigure()
            return

        #addprofile qcloudcli
        addprofile_cmd = ['addprofile']
        if module.lower() in addprofile_cmd:
            self.handleCmd.addprofile()
            return

        # useprofile qcloudcli
        useprofile_cmd = ['useprofile']
        if module.lower() in useprofile_cmd:
            self.handleCmd.useprofile()
            return

        # useprofile qcloudcli
        useprofile_cmd = ['delprofile']
        if module.lower() in useprofile_cmd:
            self.handleCmd.delprofile()
            return


        # get action,such as DescribeInterfaces
        action = self.handleParameter.getAction()

        # get paramlist
        keyValues = self.handleParameter._getKeyValues()
        outPutFormat = self.handleParameter.getUserDefinedOutPutFormat(keyValues)
        if outPutFormat is not None and len(outPutFormat) != 0:
            outPutFormat = outPutFormat[0]
        else:
            outPutFormat = self.handleCmd.getUserFormat()
            if outPutFormat is None or outPutFormat == "":
                outPutFormat = 'json'

        if self.handleData.isLegalModule(module):
            if self.handleData.isLegalAction(module, action):
                instance = self.handleData.makeInstance(module, action)
                in_class = self.handleData.makeClass(module, action)
                if instance is not None and in_class is not None:
                    helpcmds = ['-h', '--help', 'help']
                    cmdlen = self.user_input.__len__()
                    if cmdlen >= 3:
                        for i in range(2, cmdlen):
                            if self.user_input[i] in helpcmds:
                                self.showHelp.showParameterError(module, action,self.completer._help_to_show_instance_attribute(in_class)[0],self.completer._help_to_show_instance_attribute(in_class)[1])
                                return
                    if keyValues.get("RegionId") is None and keyValues.get("regionId") is None and keyValues.get("Regionid")is None and keyValues.get("regionid") is None:
                        keyValues["RegionId"] = [self.handleCmd.getUserRegion()]
                    if not self.handleData.checkInputIsEmpty(keyValues):
                        print 'Your [SecretId] or [SecretKey] or [RegionId] is absence!'
                        return
                    try:
                        outcome = self.handleData.getResponse(module, action, keyValues,instance,in_class)
                        if outcome is None:
                            return
                        result.display_result(action, outcome, outPutFormat, keyValues)
                    except Exception as e:
                        print(e)
                else:
                    print 'qcloudcli internal error, please try again.'
            else:
                self.showHelp.showActionError(module)
        else:
            self.showHelp.showModuleError()

if __name__ == '__main__':
    main()

