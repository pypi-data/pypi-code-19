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

import argparse


DEFAULT_CMDS_MAPPING = {
    'new_session_cmd': None,
    'list_sessions_cmd': None,
    'destroy_session_cmd': None,
    'new_execution_cmd': None,
    'prepare_execution_cmd': None,
    'run_execution_cmd': None,
    'collect_results_cmd': None,
    'execute_onestep_cmd': None,
    'list_executions_cmd': None
}


def get_options_parser(cmds_mapping=DEFAULT_CMDS_MAPPING):

    # create the top-level parser
    parser = argparse.ArgumentParser(prog='benchsuite')
    parser.add_argument('--verbose', '-v', action='count', help='print more information (3 levels)')
    parser.add_argument('--quiet', '-q', action='store_true', help='suppress normal output')
    parser.add_argument('--config', '-c', type=str, help='foo help')
    subparsers = parser.add_subparsers(help='sub-command help')

    parser_a = subparsers.add_parser('new-session', help='create-env help')
    parser_a.add_argument('--provider', type=str, required=True, help='bar help')
    parser_a.add_argument('--service-type', type=str, required=True, help='bar help')
    parser_a.set_defaults(func=cmds_mapping['new_session_cmd'])

    parser_a = subparsers.add_parser('list-sessions', help='a help')
    parser_a.set_defaults(func=cmds_mapping['list_sessions_cmd'])

    parser_a = subparsers.add_parser('destroy-session', help='a help')
    parser_a.add_argument('id', type=str, help='bar help')
    parser_a.set_defaults(func=cmds_mapping['destroy_session_cmd'])

    parser_a = subparsers.add_parser('new-exec', help='a help')
    parser_a.add_argument('session', type=str, help='bar help')
    parser_a.add_argument('tool', type=str, help='bar help')
    parser_a.add_argument('workload', type=str, help='bar help')
    parser_a.set_defaults(func=cmds_mapping['new_execution_cmd'])

    parser_a = subparsers.add_parser('prepare-exec', help='a help')
    parser_a.add_argument('id', type=str, help='bar help')
    parser_a.set_defaults(func=cmds_mapping['prepare_execution_cmd'])

    parser_a = subparsers.add_parser('run-exec', help='a help')
    parser_a.add_argument('id', type=str, help='bar help')
    parser_a.add_argument('--async', action='store_true', help='bar help')
    parser_a.set_defaults(func=cmds_mapping['run_execution_cmd'])


    parser_a = subparsers.add_parser('list-execs', help='lists the executions')
    parser_a.set_defaults(func=cmds_mapping['list_executions_cmd'])

    parser_a = subparsers.add_parser('collect-exec', help='collects the outputs of an execution')
    parser_a.add_argument('id', type=str, help='the execution id')
    parser_a.set_defaults(func=cmds_mapping['collect_results_cmd'])

    parser_a = subparsers.add_parser('exec', help='Execute a single benchmark test on single provider in one-step '
                                                  'execution')
    parser_a.add_argument('--provider', type=str, help='bar help')
    parser_a.add_argument('--service-type', type=str, help='bar help')
    parser_a.add_argument('--tool', type=str, help='bar help')
    parser_a.add_argument('--workload', type=str, help='bar help')
    parser_a.set_defaults(func=cmds_mapping['execute_onestep_cmd'])

    return parser
