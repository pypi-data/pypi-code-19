# vim: tabstop=4 shiftwidth=4 softtabstop=4

# Copyright (c) 2017 Cisco Systems, Inc.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import print_function

import os
import sys

import colorama
import sh


class Provisioner(object):
    def __init__(self, config):
        """A class responsible for calling ``ansible-playbook with`` the proper
        commands.

        Args:
            config (obj): An object containing our working config.
        """
        self._config = config
        colorama.init(autoreset=True)

    def _print_stdout(self, line):
        """Print to STDOUT and flush.

        Args:
            line (str): Text to be printed.
        """
        print(line, file=sys.stdout, end='')
        sys.stdout.flush()

    def _print_stderr(self, line):
        """Print to STDERR and flush.

        Args:
            line (str): Text to be printed.
        """
        print(line, file=sys.stderr, end='')
        sys.stderr.flush()

    def _construct_resume_cli(self, resume, args=sys.argv):
        """Construct a CLI string that can be used to run ``photon`` again and
        resume after an error.

        Args:
            resume (int): Position from which to resume workflow.
            args (list): List of CLI arguments used during photon execution.
        Returns:
            str: Full CLI command that can be used to resume workflow.
        """
        a = [str(i) for i in args]
        cli = os.path.basename(a[0])

        # look for an existing --resume arg and overwrite it
        try:
            location = a.index('--resume')
            a[location + 1] = str(resume)
        except ValueError:
            a.extend(['--resume', str(resume)])

        return '{} {}'.format(cli, ' '.join(a[1:]))

    def run(self, resume=1):
        """Execute ansible-playbook using information gathered from config.

        Args:
            resume (int): Used as list index - 1 from which to resume workflow.
        """
        # list index to start working on (for support of --resume)
        try:
            i = int(resume) - 1
        except ValueError:  # generally if passed a non-int
            i = 0

        cmds = self._config.playbook_cmds
        kwargs = {
            '_out': self._print_stdout,
            '_err': self._print_stderr,
            '_env': self._config.env
        }

        for counter, cmd in enumerate(cmds):
            # skip execution until we reach our --resume index
            # using a list slice doesn't work here since we need to be aware of
            # the full list to produce a resume index on failure
            if counter < i:
                continue

            try:
                sh.ansible_playbook(*cmd, **kwargs)
            except (sh.ErrorReturnCode, sh.ErrorReturnCode_1):
                msg = ('An error was encountered during playbook execution. '
                       'Please resolve manually and then use the following '
                       'command to resume execution of this script:\n\n')
                cmd = self._construct_resume_cli(counter + 1)
                print(colorama.Fore.RED + msg + cmd)
                sys.exit(1)
