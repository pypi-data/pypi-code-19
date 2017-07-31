#!/usr/bin/env python3
'''
Mimir
Mimir CLI tool
COPYRIGHT 2017 MIMIR CORPORATION
'''
import os
import sys
import logging
import getpass
from mimir_cli.strings import (
    MIMIR_DIR,
    AUTH_SUCCESS,
    ERR_NOT_AUTH,
    ERR_INVALID_CRED
)
from mimir_cli.helpers import (
    continuous_prompt,
    get_projects_list,
    INPUT_FUNCTION,
    login,
    prompt_for_project,
    read_credentials,
    submit
)
from cliff.app import App
from cliff.commandmanager import CommandManager
from cliff.command import Command
from cliff.complete import CompleteCommand

__version__ = '0.2.0'
logging.getLogger('requests').setLevel(logging.WARNING)


class Subcommand(Command):
    '''override the command class and override the take_action method'''
    log = logging.getLogger(__name__)

    def take_action(self, parsed_args):
        '''override so the subcommand can be called'''
        pass


class Version(Subcommand):
    '''prints the version number'''
    def run(self, parsed_args):
        self.app.stdout.write('mimir cli v{}\n'.format(__version__))


class New(Subcommand):
    '''the new command that allows you to create a new object on the mimir platform.'''
    def get_parser(self, prog_name):
        '''overrides the get_parser method to add an object type'''
        choices = ['project', 'lesson', 'announcement', 'test_case', 'course']
        parser = super(New, self).get_parser(prog_name)
        parser.add_argument('item_type', choices=choices)
        return parser

    def run(self, parsed_args):
        self.app.stdout.write('you want to make a new {}\n'.format(parsed_args.item_type))


class Submit(Subcommand):
    '''use this command to submit projects to the mimir platform'''
    def get_parser(self, prog_name):
        '''overrides the get_parser method to add an object type'''
        parser = super(Submit, self).get_parser(prog_name)
        parser.add_argument('-p', '--project_id', help='project_id that you wish to submit to')
        parser.add_argument('filename', help='project folder, zip, or source file')
        return parser

    def run(self, parsed_args):
        credentials = read_credentials()
        if 'auth_token' not in credentials:
            self.app.stderr.write(ERR_NOT_AUTH)
            continuous_prompt()
        filename = parsed_args.filename
        project_id = ''
        if parsed_args.project_id:
            project_id = parsed_args.project_id
        if not project_id:
            projects = get_projects_list()
            project = prompt_for_project(projects)
            project_id = project['id']
        submit(filename, project_id)


class Login(Subcommand):
    '''use this command to login to the mimir platform'''
    def get_parser(self, prog_name):
        '''overrides the get_parser method to add an object type'''
        parser = super(Login, self).get_parser(prog_name)
        parser.add_argument('-e', '--email', help='the email for your account')
        parser.add_argument('-p', '--password', help='the password for your account')
        return parser

    def run(self, parsed_args):
        email = ''
        password = ''
        if parsed_args.email:
            email = parsed_args.email
        else:
            email = INPUT_FUNCTION('Email: ')
        if parsed_args.password:
            password = parsed_args.password
        else:
            password = getpass.getpass()
        if email and password:
            success = login(email, password)
            if success:
                self.app.stdout.write(AUTH_SUCCESS)
            else:
                self.app.stderr.write(ERR_INVALID_CRED)
        else:
            self.app.stderr.write(ERR_INVALID_CRED)


class Logout(Subcommand):
    '''use this command to logout of the mimir platform'''
    def run(self, parsed_args):
        credentials_path = '{}.credentials'.format(MIMIR_DIR)
        os.remove(credentials_path)
        self.app.stdout.write('Successfully logged out of Mimir.\n')


class CLI(App):
    '''Mimir CLI object'''
    log = logging.getLogger(__name__)

    def __init__(self):
        command = CommandManager('mimir.cli')
        super(CLI, self).__init__(
            description='mimir cli application',
            version=__version__,
            command_manager=command,
        )
        commands = {
            'complete': CompleteCommand,
            'version': Version,
            'submit': Submit,
            'login': Login,
            'logout': Logout
        }
        for key, value in commands.items():
            command.add_command(key, value)

    def initialize_app(self, argv):
        self.log.debug('initialize_app')

    def prepare_to_run_command(self, cmd):
        self.log.debug('prepare_to_run_command {}'.format(cmd.__class__.__name__))

    def clean_up(self, cmd, result, err):
        self.log.debug('clean_up {}'.format(cmd.__class__.__name__))
        if err:
            self.log.debug('got an error: {}'.format(err))


def main(argv=sys.argv[1:]):
    '''main method, run cli'''
    app = CLI()
    return app.run(argv)


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
