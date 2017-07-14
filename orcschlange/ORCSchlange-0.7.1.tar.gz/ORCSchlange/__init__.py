"""The functions to handle the main function"""
from argparse import ArgumentParser, SUPPRESS

from ORCSchlange.command.fetch import FetchReporeter
from ORCSchlange.command.db import DbCommand

__version__ = "0.7.1"
"""The version of the package"""


def main():
    """The main function that loads the commands."""
    parser = ArgumentParser(prog='orcs', description="A simple tool to interact with the ORICID-Public-API.")
    
    add_global(parser)
    
    subparsers = parser.add_subparsers(metavar="The ORC-Schlange commands are:")
    fetch = subparsers.add_parser('fetch',
                                  help="""Fetch the information from the ORICID-Public-API.
                                  Call "fetch -h" for more details.""")
    
    add_fetch(fetch)
    
    db = subparsers.add_parser('db',
                               help='Manage the SQLite DB that contains the orcids. Call \"db -h\" for more details.',
                               add_help=False)
    add_db(db)
    
    args = parser.parse_args()
    args.func(args)


def add_global(parser):
    """Add the global arguments to the parser.

    :param parser: The global ArgumentParser
    """
    parser.set_defaults(func=lambda x: parser.print_help())
    parser.add_argument('--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-v', '--verbose', action='store_true', dest="verbose", help="Create verbose output")


def add_fetch(fetch):
    """Add the fetch arguments to the fetch command.

    :param fetch: The fetch ArgumentParser.
    """
    fetch.set_defaults(func=lambda args: FetchReporeter(args).fetch(), config=1)
    fetch.add_argument('--dbfile', action='store', dest="dbfile", help="The SQLite DB file that is used.",
                       default="people.db")
    fetch.add_argument('--html', action='store_false', dest="html",
                       help="Is a html output created. (default: %(default)s)")
    fetch.add_argument('--bib', action='store_true', dest="bib", help="Is a bib output created. (default: %(default)s)")
    fetch.add_argument('--path', action='store', dest="path",
                       help="The path where the output is created. (default: %(default)s)", default="output/")
    fetch.add_argument('--name', action='store', dest="name", help="The name of the output. (default: %(default)s)",
                       default="index")
    fetch.add_argument('--jQuery', action='store_true', dest="jquery",
                       help="Copy jQuery version 3.2.1 to the output path. (default: %(default)s)")
    
    api = fetch.add_argument_group(title="API-Configuration",
                                   description="""To interact with the ORCID-API the client-id and client-secret 
                                   need to set or loaded. The default is the sandbox""")
    api.add_argument("--sandbox", action='store_const', const=0, dest="config",
                     help="Run in the ORCID-Sandbox These need no further options.")
    api.add_argument("--db", action='store_const', const=1, dest="config",
                     help="Load the options out of the SQLite DB.These need that they are added before with db addAPI.")
    api.add_argument("--file", action='store', dest="config",
                     help="""Load the options out of the file that is given. These need that the file is in a json 
                     format that have a field \"client_id\" and \"client_secret\".""")
    api.add_argument("--inline", nargs=2, dest="config", help="Give the data inline. First the id then the secret.")


def add_db(db):
    """Add the db arguments and subcommands to the db command

    :param db: The db ArgumentParser.
    """
    db.set_defaults(func=lambda args: db.print_help() if not args.test else DbCommand(args).create_test())
    db.add_argument('--dbfile', action='store', dest="dbfile", help="The SQLite DB file that is used.",
                    default="people.db")
    db.add_argument('-t', '--test', action='store_true', help=SUPPRESS)
    db.add_argument('-h', "--help", action='store_true', help=SUPPRESS)
    
    dbsubs = db.add_subparsers(title="db", description="Manage the SQLite DB that contains the orcids",
                               metavar="The databank functions are:")
    
    add_dbs = dbsubs.add_parser('add', help='Add an new ORCID to the DB')
    add_dbs.add_argument('--dbfile', action='store', dest="dbfile", help="The SQLite DB file that is used.",
                         default="people.db")
    add_adddb(add_dbs)
    
    conf_db = dbsubs.add_parser('addConf', help='Add an new Config to the DB')
    conf_db.add_argument('--dbfile', action='store', dest="dbfile", help="The SQLite DB file that is used.",
                         default="people.db")
    add_conf(conf_db)
    
    print_db = dbsubs.add_parser('print', help='Print the content of the databank')
    print_db.add_argument('--dbfile', action='store', dest="dbfile", help="The SQLite DB file that is used.",
                          default="people.db")
    print_db.set_defaults(func=lambda args: DbCommand(args).prints())
    
    clean_db = dbsubs.add_parser('clean', help='Reset the databank')
    clean_db.add_argument('--dbfile', action='store', dest="dbfile", help="The SQLite DB file that is used.",
                          default="people.db")
    clean_db.set_defaults(func=lambda args: DbCommand(args).clean())
    
    create_db = dbsubs.add_parser('create', help='Create a new databank')
    create_db.add_argument('--dbfile', action='store', dest="dbfile", help="The SQLite DB file that is used.",
                           default="people.db")
    create_db.set_defaults(func=lambda args: DbCommand(args).create())


def add_adddb(add_dbs):
    """Add the arguments to the add command

    :param add_dbs: THe db add ArgumentParser.
    """
    add_dbs.add_argument('orchid', action="store", help="The new added ORCID.")
    add_dbs.add_argument('start', action="store", help="""The date after the ORCID data is 
    fetched in form "YYYY-MM-DD".""")
    add_dbs.add_argument('stop', action="store",
                         help="The date until the ORCID data is fetched in form \"YYYY-MM-DD\".",
                         nargs="?")
    add_dbs.set_defaults(func=lambda args: DbCommand(args).add())
    add_dbs.set_defaults(func=lambda args: DbCommand(args).add())


def add_conf(conf_db):
    """Add the arguments to the addConf command

     :param conf_db: THe db addConf ArgumentParser.
    """
    conf_db.add_argument('cliend_id', action="store", help="The client id of you app.")
    conf_db.add_argument('clien_secret', action="store", help="The client secret of you app.")
    conf_db.add_argument('auth', action="store", help="The url to authenticate.", nargs="?",
                         default="https://orcid.org/oauth/token")
    conf_db.add_argument('api', action="store", help="The url of the api.", nargs="?",
                         default="https://pub.orcid.org/v2.0/")
    conf_db.set_defaults(func=lambda args: DbCommand(args).add_conf())
