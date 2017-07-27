# Benchmarking Suite
# Copyright 2014-2017 Engineering Ingegneria Informatica S.p.A.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Developed in the ARTIST EU project (www.artist-project.eu) and in the
# CloudPerfect EU project (https://cloudperfect.eu/)

import logging
import sys
import traceback
from datetime import datetime

from prettytable import PrettyTable

from benchsuite.cli.argument_parser import get_options_parser
from benchsuite.core.controller import BenchmarkingController
from benchsuite.core.model.exception import BashCommandExecutionFailedException

RUNTIME_NOT_AVAILABLE_RETURN_CODE = 1

logger = logging.getLogger(__name__)


def list_benchmarks_cmd(args):
    table = PrettyTable()
    table.field_names = ["Tool", "Workloads"]
    table.align = 'l'
    with BenchmarkingController(args.config) as bc:
        for p in bc.list_available_benchmarks():
            table.add_row([p.name, '\n'.join(p.service_types)])
    print(table.get_string())


def list_providers_cmd(args):
    table = PrettyTable()
    table.field_names = ["Name", "Service Types"]
    table.align = 'l'
    with BenchmarkingController(args.config) as bc:
        for p in bc.list_available_providers():
            table.add_row([p.name, ', '.join(p.service_types)])
    print(table.get_string())


def list_executions_cmd(args):

    table = PrettyTable()
    table.field_names = ["Id", "Benchmark", "Created", "Exec. Env.", "Session"]

    with BenchmarkingController(args.config) as bc:
        execs = bc.list_executions()
        for e in execs:
            created = datetime.fromtimestamp(e.created).strftime('%Y-%m-%d %H:%M:%S')
            table.add_row([e.id, e.test.name, created, e.exec_env, e.session.id])

    print(table.get_string())


def list_sessions_cmd(args):

    table = PrettyTable()
    table.field_names = ["Id", "Provider", "Service Type", "Created"]

    with BenchmarkingController(args.config) as bc:
        sessions = bc.list_sessions()
        for s in sessions:
            created = datetime.fromtimestamp(s.created).strftime('%Y-%m-%d %H:%M:%S')
            table.add_row([s.id, s.provider.name, s.provider.service_type, created])

        print(table.get_string())


def destroy_session_cmd(args):
    with BenchmarkingController(args.config) as bc:
        bc.destroy_session(args.id)
        print('Session {0} successfully destroyed'.format(args.id))


def new_session_cmd(args):
    with BenchmarkingController(args.config) as bc:
        e = bc.new_session(args.provider, args.service_type)
        print(e.id)


def new_execution_cmd(args):
    with BenchmarkingController(args.config) as bc:
        e = bc.new_execution(args.session, args.tool, args.workload)
        print(e.id)


def prepare_execution_cmd(args):
    with BenchmarkingController(args.config) as bc:
        bc.prepare_execution(args.id)


def collect_results_cmd(args):
    with BenchmarkingController(args.config) as bc:
        out, err = bc.collect_execution_results(args.id)
        print(str(out))
        print(str(err))


def run_execution_cmd(args):
    with BenchmarkingController(args.config) as bc:
        bc.run_execution(args.id, async=args.async)


def execute_onestep_cmd(args):
    with BenchmarkingController() as bc:
        out, err = bc.execute_onestep(args.provider, args.service_type, args.tool, args.workload)
        print('============ STDOUT ============')
        print(out)
        print('============ STDERR ============')
        print(err)



def main(args=None):

    cmds_mapping = {
        'new_session_cmd': new_session_cmd,
        'list_sessions_cmd': list_sessions_cmd,
        'destroy_session_cmd': destroy_session_cmd,
        'new_execution_cmd': new_execution_cmd,
        'prepare_execution_cmd': prepare_execution_cmd,
        'run_execution_cmd': run_execution_cmd,
        'collect_results_cmd': collect_results_cmd,
        'execute_onestep_cmd': execute_onestep_cmd,
        'list_executions_cmd': list_executions_cmd,
        'list_providers_cmd': list_providers_cmd,
        'list_benchmarks_cmd': list_benchmarks_cmd
    }

    parser = get_options_parser(cmds_mapping=cmds_mapping)

    args = parser.parse_args(args = args or sys.argv[1:])

    # adjust logging to the console accordingly with the verbosity level requested
    #
    # FATAL
    # CRITICAL
    # ERROR
    # WARNING
    # INFO -v
    # DEBUG -vv
    # DEBUG (all modules) -vvv

    logging_level = logging.WARNING
    logging_format = '%(message)s'

    if args.verbose:
        if args.verbose == 1:
            logging_level = logging.INFO
            logging_format = '%(message)s'

        if args.verbose == 2:
            logging_level = logging.DEBUG
            logging_format = '%(message)s'

        if args.verbose > 2:
            logging_level = logging.DEBUG
            logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


    # if the user sets the --quiet flag, do not print logging messages. Only print() messages will appear on the screen
    if args.quiet:
        logging.basicConfig(stream=None)

    else:

        # basic config for all loggers (included the ones from third-party libs)
        logging.basicConfig(
            level=logging.ERROR,
            stream=sys.stdout,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # logging from benchsuite modules
        st = logging.StreamHandler(stream=sys.stdout)
        st.setLevel(logging_level)
        st.setFormatter(logging.Formatter(logging_format))
        bench_suite_loggers = logging.getLogger('benchsuite')
        bench_suite_loggers.addHandler(st)
        bench_suite_loggers.setLevel(logging_level)
        bench_suite_loggers.propagate = False

        if args.verbose  and args.verbose > 2:
            logging.root.setLevel(logging.DEBUG)


    try:
        args.func(args)
    except BashCommandExecutionFailedException as e:
        print(str(e))
        error_file = 'last_cmd_error.dump'
        with open(error_file, "w") as text_file:
            text_file.write("========== CMD ==========\n")
            text_file.write(e.cmd)
            text_file.write('\n\n>>> Exit status was {0}\n'.format(e.exit_status))
            text_file.write("\n\n========== STDOUT ==========\n")
            text_file.write(e.stdout)
            text_file.write("\n\n========== STDERR ==========\n")
            text_file.write(e.stderr)

        print('Command stdout and stderr have been dumped to {0}'.format(error_file))
        sys.exit(1)

    except Exception as e:
        print('ERROR!!! An exception occured: "{0}" (run with -v to see the stacktrace)'.format(str(e)))
        if args.verbose and args.verbose > 0:
            traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])