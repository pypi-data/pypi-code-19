#!/usr/bin/env python


def add_executions_args(subparsers):
    root_parser_name = 'executions'
    parser_executions = subparsers.add_parser('executions', help='Manages executions')
    executions = parser_executions.add_subparsers(help='Manage executions',
                                                  dest=root_parser_name)

    list = executions.add_parser('list', help='List executions')
    list.add_argument('-i', '--include_completed',
                      action='store_true',
                      help='List all executions (include completed)')
    list.add_argument('-d', '--deployment',
                      action="store",
                      help='Retrieve executions for given deployment')

    get = executions.add_parser('get', help='Get executions status')
    get.add_argument('uuid',
                     action="store",
                     help='The execution uuid to retrieve')
    get.add_argument('-w', '--wait',
                     action='store_true',
                     help='Wait for completion')

    get_bulk = executions.add_parser('get_bulk', help='Get executions status')
    get_bulk.add_argument('-u', '--uuid',
                          action="append",
                          nargs='*',
                          help='The executions uuid to retrieve')

    cancel = executions.add_parser('cancel', help='Cancel executions')
    cancel.add_argument('uuid',
                        action="store",
                        help='The executions uuid to cancel')

    return root_parser_name
