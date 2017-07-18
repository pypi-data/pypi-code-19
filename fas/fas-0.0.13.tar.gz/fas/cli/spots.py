#!/usr/bin/env python


def add_spots_args(subparsers):
    root_parser_name = 'spots'
    parser_spots = subparsers.add_parser('spots', help='Manage spots')
    spots = parser_spots.add_subparsers(help='Manage spots',
                                        dest=root_parser_name)

    spots.add_parser('list', help='List spots')

    add = spots.add_parser('add',
                           help='Increase the number of spots by one')
    add.add_argument('-w', '--wait',
                     action='store_true',
                     help='Wait for creation')

    get = spots.add_parser('get', help='Get status on a spot')
    get.add_argument('ip',
                     action="store",
                     help='Specify spot ip to delete')

    remove = spots.add_parser('remove',
                              help='Reduce the number of spots by one')
    remove.add_argument('-i', '--ip',
                        action="store",
                        help='Specify which spot to remove')
    remove.add_argument('-w', '--wait',
                        action='store_true',
                        help='Wait for deletion')

    update = spots.add_parser('update', help='Update spot parameters')
    update.add_argument('--min',
                        action="store",
                        help='Specify minimum amount of workers in a spot')
    update.add_argument('--max',
                        action="store",
                        help='Specify maximum amount of workers in a spot')

    refresh_ip = spots.add_parser('refresh_ip', help='Refresh spot instances ip')
    refresh_ip.add_argument('-w', '--wait',
                            action='store_true',
                            help='Wait for deletion')
    refresh_ip.add_argument('-i', '--ip',
                            action="store",
                            help='Specify which spot to remove')

    replace = spots.add_parser('replace',
                               help='Remove spot and create another one instead')
    replace.add_argument('ip',
                         action="store",
                         help='Specify which spot to replace')

    return root_parser_name
