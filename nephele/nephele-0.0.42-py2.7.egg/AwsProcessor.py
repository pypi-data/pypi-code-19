from SilentException import SilentException
from SlashException import SlashException

from stdplusAwsHelpers.AwsConnectionFactory import AwsConnectionFactory
from CommandArgumentParser import *
from stdplus import *

import cmd
import json
import os
import re
import signal
import sys
import traceback
import Config
from botocore.exceptions import ClientError
from pprint import pprint

def sshAddress(address,forwarding,replaceKey,keyscan,background,verbosity=0,command=None,ignoreHostKey=False,echoCommand=True,name=''):
    if replaceKey or keyscan:
        resetKnownHost(address)

    if keyscan:
        keyscanHost(address)

    args=["/usr/bin/ssh",address]
    if ignoreHostKey:
        args.extend(["-o","StrictHostKeyChecking=no",
                     "-o","UpdateHostKeys=yes"])
        
    if not forwarding == None:
        for forwardInfo in forwarding:
            if isInt(forwardInfo):
                forwardInfo = "{0}:localhost:{0}".format(forwardInfo)
            args.extend(["-L",forwardInfo])
        if background:
            args.extend(["-N","-n"])
    else:
        background = False # Background is ignored if not forwarding

    if verbosity > 0:
        args.append("-" + "v" * verbosity)

    if 'ssh-jump-host' in Config.config['selectedProfile']:
        if 'ssh-jump-user' in Config.config['selectedProfile']:
            args.extend(["-q", "-J",'{}@{}'.format(Config.config['selectedProfile']['ssh-jump-user'],Config.config['selectedProfile']['ssh-jump-host'])])
        else:
            args.extend(["-q", "-J",Config.config['selectedProfile']['ssh-jump-host']])

    if command:
        args.append(command)

    if echoCommand:
        print "{}{}".format(name," ".join(args))
        
    pid = fexecvp(args)
    if background:
        print "SSH Started in background. pid:{}".format(pid)
        AwsProcessor.backgroundTasks.append(pid)
    else:
        os.waitpid(pid,0)
   

def ssh(instanceId,interfaceNumber,forwarding,replaceKey,keyscan,background,verbosity=0,command=None,ignoreHostKey=False,echoCommand=True,name=''):
    if isIp(instanceId):
        sshAddress(instanceId,forwarding,replaceKey,keyscan,background,verbosity,command,ignoreHostKey=ignoreHostKey)
    else:
        client = AwsConnectionFactory.getEc2Client()
        response = client.describe_instances(InstanceIds=[instanceId])
        networkInterfaces = response['Reservations'][0]['Instances'][0]['NetworkInterfaces'];
        if None == interfaceNumber:
            number = 0
            for interface in networkInterfaces:
                print "{0:3d} {1}".format(number,interface['PrivateIpAddress'])
                number += 1
        else:
            address = "{}".format(networkInterfaces[interfaceNumber]['PrivateIpAddress'])
            sshAddress(address,forwarding,replaceKey,keyscan,background,verbosity,command,ignoreHostKey=ignoreHostKey,echoCommand=echoCommand,name=name)

class AwsProcessor(cmd.Cmd):
    backgroundTasks=[]
    resourceTypeAliases={ 'AWS::AutoScaling::AutoScalingGroup' : 'asg',
                          'AWS::CloudFormation::Stack' : 'stack',
                          'AWS::EC2::NetworkInterface' : 'eni',
                          'AWS::Logs::LogGroup' : 'logGroup' }
    processorFactory = None
    
    def __init__(self,prompt,parent):
        cmd.Cmd.__init__(self)
        self.raw_prompt = prompt
        self.prompt = prompt + "/: "
        self.parent = parent

    def emptyline(self):
        pass

    @staticmethod
    def killBackgroundTasks():
        for pid in AwsProcessor.backgroundTasks:
            print "Killing pid:{}".format(pid)
            os.kill(pid,signal.SIGQUIT)
    
    def onecmd(self, line):
        try:
            return cmd.Cmd.onecmd(self,line)
        except SystemExit, e:
            raise e;
        except SlashException, e:
            if None == self.parent:
                pass
            else:
                raise e
        except SilentException:
            pass
        except ClientError as e:
            # traceback.print_exc()
            if e.response['Error']['Code'] == 'AccessDenied':
                print "ERROR: Access Denied. Maybe you need to run mfa {code}"
                traceback.print_exc()
        except Exception, other:
            traceback.print_exc()
        except:
            print "Unexpected error:", sys.exc_info()[0]

    def mfa_devices(self, awsProfile='default'):
        list_mfa_devices_command = ["aws","--profile",awsProfile,"--output","json","iam","list-mfa-devices"]
        result = run_cmd(list_mfa_devices_command)
        if result.retCode == 0 :
            return json.loads("\n".join(result.stdout))['MFADevices']
        else:
            raise Exception('There was a problem fetching MFA devices from AWS')
            
    def load_arn_from_aws(self, awsProfile):
        devices = self.mfa_devices(awsProfile)
        if len(devices):
            return devices[0]['SerialNumber']
        else:
            raise Exception('No MFA devices were found for your account')

    def do_mfa(self, args):
        """
        Enter a 6-digit MFA token. Nephele will execute the appropriate
        `aws` command line to authenticate that token. 

        mfa -h for more details
        """
        
        parser = CommandArgumentParser("mfa")
        parser.add_argument(dest='token',help='MFA token value');
        parser.add_argument("-p","--profile",dest='awsProfile',default=AwsConnectionFactory.instance.getProfile(),help='MFA token value');
        args = vars(parser.parse_args(args))

        token = args['token']
        awsProfile = args['awsProfile']
        arn = AwsConnectionFactory.instance.load_arn(awsProfile)

        credentials_command = ["aws","--profile",awsProfile,"--output","json","sts","get-session-token","--serial-number",arn,"--token-code",token]
        output = run_cmd(credentials_command) # Throws on non-zero exit :yey:

        credentials = json.loads("\n".join(output.stdout))['Credentials']
        AwsConnectionFactory.instance.setMfaCredentials(credentials,awsProfile)

    def do_up(self,args):
        """
        Navigate up by one level.

        For example, if you are in `(aws)/stack:.../asg:.../`, executing `up` will place you in `(aws)/stack:.../`.

        up -h for more details
        """
        parser = CommandArgumentParser("up")
        args = vars(parser.parse_args(args))
        if None == self.parent:
            print "You're at the root. Try 'quit' to quit"
        else:
            return True

    def do_slash(self,args):
        """
        Navigate back to the root level.

        For example, if you are in `(aws)/stack:.../asg:.../`, executing `slash` will place you in `(aws)/`.

        slash -h for more details
        """
        parser = CommandArgumentParser("slash")
        args = vars(parser.parse_args(args))
        if None == self.parent:
            print "You're at the root. Try 'quit' to quit"
        else:
            raise SlashException()

    def do_profile(self,args):
        """
        Select nephele profile

        profile -h for more details
        """
        parser = CommandArgumentParser("profile")
        parser.add_argument(dest="profile",help="Profile name")
        parser.add_argument('-v','--verbose',dest="verbose",action='store_true',help='verbose')
        args = vars(parser.parse_args(args))

        profile = args['profile']
        verbose = args['verbose']
        if verbose:
            print "Selecting profile '{}'".format(profile)

        selectedProfile = {}
        if profile in Config.config['profiles']:
            selectedProfile = Config.config['profiles'][profile]

        selectedProfile['name'] = profile
        Config.config['selectedProfile'] = selectedProfile

        awsProfile = profile
        if 'awsProfile' in selectedProfile:
            awsProfile = selectedProfile['awsProfile']
        AwsConnectionFactory.resetInstance(profile=awsProfile)

    def do_quit(self,args):
        """
        Exit nephele
        """
        raise SystemExit

    def childLoop(self,child):
        try:
            child.cmdloop()
        except SilentException, e:
            raise e
        except SlashException, e:
            raise e
        except Exception, e:
            print "Exception: {}".format(e)
            traceback.print_exc()

    def stackResource(self,stackName,logicalId):
        print "loading stack resource {}.{}".format(stackName,logicalId)
        stackResource = AwsConnectionFactory.instance.getCfResource().StackResource(stackName,logicalId)
        pprint(stackResource)
        if "AWS::CloudFormation::Stack" == stackResource.resource_type:
            pprint(stackResource)
            print "Found a stack w/ physical id:{}".format(stackResource.physical_resource_id)
            childStack = AwsConnectionFactory.instance.getCfResource().Stack(stackResource.physical_resource_id)
            print "Creating prompt"
            self.childLoop(AwsProcessor.processorFactory.Stack(childStack,logicalId,self))
        elif "AWS::AutoScaling::AutoScalingGroup" == stackResource.resource_type:
            scalingGroup = stackResource.physical_resource_id
            self.childLoop(AwsProcessor.processorFactory.AutoScalingGroup(scalingGroup,self))
        elif "AWS::EC2::NetworkInterface" == stackResource.resource_type:
            eniId = stackResource.physical_resource_id
            self.childLoop(AwsProcessor.processorFactory.Eni(eniId,self))
        elif "AWS::Logs::LogGroup" == stackResource.resource_type:
            self.childLoop(AwsProcessor.processorFactory.LogGroup(stackResource,self))
        elif "AWS::IAM::Role" == stackResource.resource_type:
            self.childLoop(AwsProcessor.processorFactory.Role(stackResource,self))
        else:
            pprint(stackResource)
            print("- description:{}".format(stackResource.description))
            print("- last_updated_timestamp:{}".format(stackResource.last_updated_timestamp))
            print("- logical_resource_id:{}".format(stackResource.logical_resource_id))
            print("- metadata:{}".format(stackResource.metadata.strip()))
            print("- physical_resource_id:{}".format(stackResource.physical_resource_id))
            print("- resource_status:{}".format(stackResource.resource_status))
            print("- resource_status_reason:{}".format(stackResource.resource_status_reason))
            print("- resource_type:{}".format(stackResource.resource_type))
            print("- stack_id:{}".format(stackResource.stack_id))

    def do_ssh(self,args):
        """
        SSH to an instance. 

        Note: This command is extended in more specific contexts, for example inside Autoscaling Groups

        ssh -h for more details
        """
        parser = CommandArgumentParser("ssh")
        parser.add_argument(dest='id',help='identifier of the instance to ssh to [aws instance-id or ip address]')
        parser.add_argument('-a','--interface-number',dest='interface-number',default='0',help='instance id of the instance to ssh to')
        parser.add_argument('-ii','--ignore-host-key',dest='ignore-host-key',default=False,action='store_true',help='Ignore host key')
        parser.add_argument('-ne','--no-echo',dest='no-echo',default=False,action='store_true',help='Do not echo command')
        parser.add_argument('-L',dest='forwarding',nargs='*',help="port forwarding string: {localport}:{host-visible-to-instance}:{remoteport} or {port}")
        parser.add_argument('-R','--replace-key',dest='replaceKey',default=False,action='store_true',help="Replace the host's key. This is useful when AWS recycles an IP address you've seen before.")
        parser.add_argument('-Y','--keyscan',dest='keyscan',default=False,action='store_true',help="Perform a keyscan to avoid having to say 'yes' for a new host. Implies -R.")
        parser.add_argument('-B','--background',dest='background',default=False,action='store_true',help="Run in the background. (e.g., forward an ssh session and then do other stuff in aws-shell).")
        parser.add_argument('-v',dest='verbosity',default=0,action=VAction,nargs='?',help='Verbosity. The more instances, the more verbose');
        parser.add_argument('-m',dest='macro',default=False,action='store_true',help='{command} is a series of macros to execute, not the actual command to run on the host');
        parser.add_argument(dest='command',nargs='*',help="Command to run") 
        args = vars(parser.parse_args(args))

        targetId = args['id']
        interfaceNumber = int(args['interface-number'])
        forwarding = args['forwarding']
        replaceKey = args['replaceKey']
        keyscan = args['keyscan']
        background = args['background']
        verbosity = args['verbosity']
        ignoreHostKey = args['ignore-host-key']
        noEcho = args['no-echo']
        
        if args['macro']:
            if len(args['command']) > 1:
                print("Only one macro may be specified with the -m switch.")
                return
            else:
                macro = args['command'][0]
                print("Macro:{}".format(macro))
                command = Config.config['ssh-macros'][macro]
        else:
            command = ' '.join(args['command'])
        
        ssh(targetId,interfaceNumber, forwarding, replaceKey, keyscan, background, verbosity, command, ignoreHostKey=ignoreHostKey, echoCommand = not noEcho)

    def do_config(self,args):
        """
        Deal with configuration. Available subcommands:

        * config print - print the current configuration
        * config reload - reload the current configuration from disk
        * config set - change a setting in the configuration
        * config save - save the configuration to disk

        config -h for more details
        """
        parser = CommandArgumentParser("config")
        subparsers = parser.add_subparsers(help='sub-command help',dest='command')
        # subparsers.required=
        subparsers._parser_class = argparse.ArgumentParser # This is to work around `TypeError: __init__() got an unexpected keyword argument 'prog'`
        
        parserPrint = subparsers.add_parser('print',help='Print the current configuration')
        parserPrint.add_argument(dest='keys',nargs='*',help='Key(s) to print')
        
        parserSet = subparsers.add_parser('set',help='Set a configuration value')
        parserSave = subparsers.add_parser('save',help='Save the current configuration')
        parserReload = subparsers.add_parser('reload',help='Reload the configuration from disk')
        args = vars(parser.parse_args(args))

        print("Command:{}".format(args['command']))
        {
            'print' : AwsProcessor.sub_configPrint,
            'set' : AwsProcessor.sub_configSet,
            'save' : AwsProcessor.sub_configSave,
            'reload' : AwsProcessor.sub_configReload
        }[args['command']]( self, args )

    def sub_configPrint(self,args):
        if not args['keys']:
            print("Current configuration:{}".format(Config.config))
        else:
            for key in args['keys']:
                subkeys = key.split('.')
                entry = Config.config
                for subkey in subkeys:
                    if subkey in entry:
                        entry = entry[subkey]
                    else:
                        entry = None
                print "{}: {}".format(key,entry)

    def sub_configSet(self,args):
        print("Set configuration:{}".format(args))
        
    def sub_configSave(self,args):
        print("Save configuration:{}".format(args))

    def sub_configReload(self,args):
        Config.loadConfig()
