from keyman.commands.basecommand import Command
from keyman.commands.recover import RecoverCommand
from keyman.entities import ArgStruct


class RemoveCommand(Command):
    name = 'remove'

    parser_kw = {
        'help': "Remove an existing account / accounts.",
        'description': 'Remove an account / accounts designated by id(s).'
    }

    arguments = [
        ArgStruct(
            "-i", "--id",
            nargs="+",
            type=int,
            # required=True,
            metavar=("ID1", "ID2"),
            help="the ids of the accounts to be removed",
            dest="ids"
        ),
        ArgStruct(
            "--nontrash",
            action="store_true",
            help="Don't move the record into trash, but remove it from the "
                 "dababase completely.",
            dest="nontrash"
        )
    ]

    def __init__(self, **kwargs):
        super(RemoveCommand, self).__init__()
        self.ids = kwargs.get("ids", [])
        self.nontrash = kwargs.get("nontrash", False)

    def run(self, dbhandler):
        n_removed = 0

        if not self.ids:  # 0-len
            print("No ids given. Use --help or -h to learn about the usage.")
            return

        for i in self.ids:
            n_removed += dbhandler.remove(i, self.nontrash)

        if n_removed == 0:
            print("No account record was changed.")
            return

        if self.nontrash:
            print("{0} account record{1} been removed completely.".format(
                n_removed,
                " has" if n_removed in (0, 1) else "s have"
            ))
        else:
            print(
                '{0} account record{1} been moved into trash. You can '
                'recover it with sub-command "{2}" at any time.'.format(
                    n_removed,
                    " has" if n_removed in (0, 1) else "s have",
                    RecoverCommand.name
                )
            )

        return 0
