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
    table.field_names = ["Id", "Type", "Created"]

    with BenchmarkingController(args.config) as bc:
        sessions = bc.list_sessions()
        for s in sessions:
            created = datetime.fromtimestamp(s.created).strftime('%Y-%m-%d %H:%M:%S')
            table.add_row([s.id, s.provider.type, created])

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
        'list_executions_cmd': list_executions_cmd
    }

    parser = get_options_parser(cmds_mapping=cmds_mapping)

    args = parser.parse_args(args = args or sys.argv[1:])


    # default
    logging_level = logging.INFO
    logging_format = '%(message)s'


    if args.quiet:
        logging_level = logging.ERROR
        logging_format = '%(message)s'

    if args.verbose:
        if args.verbose == 1:
            logging_level = logging.DEBUG
            logging_format = '%(message)s'

        if args.verbose > 1:
            logging_level = logging.DEBUG
            logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'



    bench_suite_loggers = logging.getLogger('benchsuite')

    logging.basicConfig(
        level=logging.CRITICAL,
        stream=sys.stdout,
        format=logging_format)

    bench_suite_loggers.setLevel(logging_level)

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
        if args.verbose > 0:
            traceback.print_exc()


if __name__ == '__main__':
    main(sys.argv[1:])