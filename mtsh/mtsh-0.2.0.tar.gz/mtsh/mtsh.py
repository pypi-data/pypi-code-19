# -*- coding: utf-8 -*-

# imports
import subprocess
import sys
import re

# mtsh class
class mtsh:

    # main constructor
    def __init__ (self, servers):
        # initialze the server list
        self.servers = servers
        # validate ourselves
        self.validate()

    # validate passed info
    # meant to be only unsafe method
    # that throws any exceptions
    def validate (self):
        # loop over all servers
        for server in self.servers:
            # server entry is not in valid form
            if not re.match(r"^[A-Za-z0-9_]*\@[A-Za-z0-9_\.]*$", server):
                # raise an exception
                raise Exception(server + " is not a valid server connection entry")
        # split domains off from entries and store
        domains = [server.split("@")[1] for server in self.servers]
        # there are duplicate domain entries
        if len(domains) > len(set(domains)):
            # raise an exception
            raise Exception("All server connection entries must have a unique domain")

    # perform command
    # returns a dictionary
    # keys in dictionary correspond to command output
    # item at each key is an array
    # first element in array is a boolean, declaring if the output is an error
    # all other elements are the names of the server connections that match the output
    def command (self, command):
        # results dictionary
        results = {}
        # loop over all servers
        for server in self.servers:
            # perform the ssh command
            ssh = subprocess.Popen(["ssh", "%s" % server, command],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE,
                                    shell=False)
            # store the output along with errors
            stdout = ssh.stdout.read()
            stderr = ssh.stderr.read()
            output = stdout + stderr
            # if output exists in results
            if output in results.keys():
                # update the relevant servers
                results[output].append(server)
            # if output does not exist in results
            else:
                # initialize the output server list
                # along with error boolean
                results[output] = [len(stderr) > 0, server]
        # return the results
        return results
