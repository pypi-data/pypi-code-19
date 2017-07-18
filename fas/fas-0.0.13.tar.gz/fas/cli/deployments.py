#!/usr/bin/env python


def add_deployments_args(subparsers):
    root_parser_name = 'deployments'
    parser_deployments = subparsers.add_parser('deployments', help='Manage deployments')
    deployments = parser_deployments.add_subparsers(help='Manage deployments',
                                                    dest=root_parser_name)

    deployments.add_parser('list', help='List deployments')

    get = deployments.add_parser('get', help='Get a deployment')
    get.add_argument('name',
                     action="store",
                     help='The deployment name to retrieve')
    # When using the cli, call the `get` command with pretty_print argument
    get.set_defaults(pretty_print=True)

    create = deployments.add_parser('create', help='Create a new deployment')
    create.add_argument('name',
                        action="store",
                        help='The name of the deployment')
    create.add_argument('--file',
                        type=file,
                        help='The file code',
                        required=True)
    create.add_argument('-r', '--requirements-file',
                        type=file,
                        help='The requirements file',
                        dest="requirements_file",
                        required=False)
    create.add_argument('-c', '--context-file',
                        type=file,
                        help='The requirements file',
                        dest="context_file",
                        required=False)
    create.add_argument('-w', '--wait',
                        action='store_true',
                        help='Wait for creation')

    update = deployments.add_parser('update', help='Update an existing deployment')
    update.add_argument('name',
                        action="store",
                        help='The name of the deployment')
    update.add_argument('-f', '--file',
                        type=file,
                        help='The code file',
                        dest="file_obj",
                        required=False)
    update.add_argument('-r', '--requirements-file',
                        type=file,
                        help='The requirements file',
                        dest="requirements_file",
                        required=False)
    update.add_argument('-c', '--context-file',
                        type=file,
                        help='The requirements file',
                        dest="context_file",
                        required=False)
    update.add_argument('-n', '--new-name',
                        action="store",
                        dest="new_name",
                        help='New name for the deployment')
    update.add_argument('-w', '--wait',
                        action='store_true',
                        help='Wait for completion')

    delete = deployments.add_parser('delete', help='Delete a deployment')
    delete.add_argument('name',
                        action="store",
                        help='The deployment name to delete')

    run = deployments.add_parser('run', help='Run an existing deployment')
    run.add_argument('name',
                     action="store",
                     help='The name of the deployment')
    run.add_argument('-p', '--parameters',
                     action="store",
                     help='Function parameters, list of key=value',
                     nargs='*',
                     required=False)
    run.add_argument('-w', '--wait',
                     action='store_true',
                     help='Wait for completion')
    run.add_argument('-i', '--interval',
                     type=float,
                     default=5,
                     action='store',
                     dest="interval",
                     help='An interval sleep, in seconds, between retry')

    samples = deployments.add_parser('samples', help='Create a sample function')
    samples_options = samples.add_mutually_exclusive_group()
    samples_options.add_argument('--hello',
                                 action="store_true",
                                 help='Generate hello-world function')
    samples_options.add_argument('--fib',
                                 action="store_true",
                                 help='Generate fibonacci function')
    samples_options.add_argument('--ping',
                                 action="store_true",
                                 help='Generate ping function')
    return root_parser_name
