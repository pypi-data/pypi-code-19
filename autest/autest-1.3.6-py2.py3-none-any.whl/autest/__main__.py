
from __future__ import absolute_import, division, print_function

import sys
import os

import hosts
import hosts.output

import autest
import autest.core.testrun
from autest.core.engine import Engine
import autest.common.execfile as execfile

from autest.common.settings import Settings, JobValues
from autest.core.variables import Variables
import autest.api as api


def main():
    # create primary commandline parser
    setup = Settings()

    setup.path_argument(
        ["-D", "--directory"],
        default=os.path.abspath('.'),
        help="The directory with all the tests in them")

    setup.path_argument(
        ["--autest-site"],
        help="A user provided autest-site directory to use instead of the default")

    setup.path_argument(
        ["--sandbox"],
        default=os.path.abspath('./_sandbox'),
        exists=False,
        help="The root directory in which the tests will run")

    setup.add_argument(
        ["-j", "--jobs"],
        default=1,
        type=JobValues,
        help="The number of test to try to run at the same time")

    setup.list_argument(
        ["--env"],
        metavar="Key=Value",
        help="Set a variable to be used in the local test environment. Replaces value inherited from shell.")

    setup.list_argument(
        ["-f", "--filters"],
        dest='filters',
        default=['*'],
        help="Filter the tests run by their names")

    setup.list_argument(
        ["-R", "--reporters"],
        default=['default'],
        help="Names of Reporters to use for report generation")

    setup.add_argument(
        ['-V', '--version'], action='version',
        version='%(prog)s {0}'.format(autest.__version__))

    # this is a commandline tool so make the cli host
    hosts.setDefaultArgs(setup.parser)
    # make default host
    myhost = hosts.ConsoleHost(setup.parser)
    # setup the extended streams to run
    hosts.Setup(myhost)

    # parser should have all option defined by program and or host type defined
    setup.partial_parse()
    hosts.output.WriteDebugf(
        "init", "Before extension load: args = {0}\n unknown = {1}", setup.arguments, setup.unknowns)
    # -------------------------------------------
    # setup vars
    variables = Variables({
        'Autest': Variables({
            ########################
            # Process Control
            # Long delay before process trees are shut down
            'StopProcessLongDelaySeconds': 10,
            #  Short delay after first process kill before next will be kill
            'StopProcessShortDelaySeconds': 1,
            #  delay after control-c before kill
            'KillDelaySecond': 1,

            ########################
            # Process Spawning

            # False -> autoselect logic used
            # True -> Use shell, Bad commands don't report clearly
            'ForceUseShell': None
        })
    })

    # setup shell environment
    env = os.environ.copy()
    if setup.arguments.env:
        for i in setup.arguments.env:
            try:
                k, v = i.split("=", 1)
                env[k] = v
            except ValueError:
                hosts.output.WriteWarning(
                    "--env value '{0}' ignored. Needs to in the form of Key=Value".format(i))
    # -------------------------------------------
    # look in autest-site directory to see if we have a file to define user
    # options
    if setup.arguments.autest_site is None:
        # this is the default
        path = os.path.join(setup.arguments.directory, 'autest-site')
    else:
        # This is a custom location
        path = os.path.abspath(setup.arguments.autest_site)

    old_path = sys.path[:]
    sys.path.append(path)
    # see if we have a file to load to get new options
    options_file = os.path.join(path, "init.cli.ext")
    if os.path.exists(options_file):
        _locals = {
            'Settings': setup,
            'AutestSitePath': path,
            "host": hosts.output,
            'AuTestVersion': api.AuTestVersion,
        }
        execfile.execFile(options_file, _locals, _locals)
    # parse the options and error if we have unknown options
    setup.final_parse()
    hosts.output.WriteDebugf(
        "init", "After extension load: args = {0}", setup.arguments)

    # see if we have any custom setup we want to do globally.
    options_file = os.path.join(path, "setup.cli.ext")
    if os.path.exists(options_file):
        _locals = {
            'os': os,
            'ENV': env,
            'Variables': variables,
            'Arguments': setup.arguments,
            "host": hosts.output,
            'AutestSitePath': path,
            'AuTestVersion': api.AuTestVersion,
        }
        execfile.execFile(options_file, _locals, _locals)
    sys.path = old_path
    # this is a cli program so we only make one engine and run it
    # a GUI might make a new GUI for every run as it might have new options,
    # or maybe not
    myEngine = Engine(jobs=setup.arguments.jobs,
                      test_dir=setup.arguments.directory,
                      run_dir=setup.arguments.sandbox,
                      autest_site=setup.arguments.autest_site,
                      filters=setup.arguments.filters,
                      reporters=setup.arguments.reporters,
                      env=env,
                      variables=variables)

    try:
        ret = myEngine.Start()
    except SystemExit:
        hosts.output.WriteError("Autest shutdown because of critical error!",exit=False,show_stack=False)
        ret = 1
    exit(ret)


if __name__ == '__main__':
    main()
