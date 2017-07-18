#!/usr/bin/env python


def add_profiles_args(subparsers):
    root_parser_name = 'profiles'
    parser_profiles = subparsers.add_parser('profiles', help='Manage profiles')
    profiles = parser_profiles.add_subparsers(help='Manage profiles',
                                              dest=root_parser_name)

    list = profiles.add_parser('list', help='List profiles')
    list.add_argument('-a', '--all',
                      action='store_true',
                      help='List all profiles')

    create = profiles.add_parser('create',
                                 help='Create a new profile')
    create.add_argument('name',
                        action="store",
                        help='The profile name')
    create.add_argument('-u', '--username',
                        action="store",
                        help='Specify FaaSpot username')
    create.add_argument('-p', '--password',
                        action="store",
                        help='Specify FaaSpot password')
    create.add_argument('-t', '--token',
                        action="store",
                        help='Specify FaaSpot API Token')
    create.add_argument('--update-if-exist',
                        action='store_true',
                        help='Update existing profile, if already exists')

    update = profiles.add_parser('update',
                                 help='update exiting profile')
    update.add_argument('name',
                        action="store",
                        help='The profile name')
    update.add_argument('-t', '--token',
                        action="store",
                        dest="token",
                        help='Specify FaaSpot token')
    update.add_argument('-u', '--username',
                        action="store",
                        help='Specify FaaSpot username')
    update.add_argument('-p', '--password',
                        action="store",
                        help='Specify FaaSpot password')

    get = profiles.add_parser('get',
                              help='Return the profile info')
    get.add_argument('name',
                     action="store",
                     help='The profile name (default id the current profile)')

    use = profiles.add_parser('use',
                              help='Set the profile to use')
    use.add_argument('name',
                     action="store",
                     help='The profile name to use')

    profiles.add_parser('current',
                        help='Show current profile info')

    delete = profiles.add_parser('delete', help='Delete a profile')
    delete.add_argument('name',
                        action="store",
                        help='The profile name to use')

    return root_parser_name
