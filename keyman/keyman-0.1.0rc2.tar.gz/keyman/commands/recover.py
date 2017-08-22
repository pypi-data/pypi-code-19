from keyman.commands.basecommand import Command
from keyman.entities import ArgStruct


class RecoverCommand(Command):
    name = 'recover'

    parser_kw = {
        'help': 'Recover an account / accounts designated by "id" from trash.',
        'description': "Recover an existing account / accounts that has been "
                       "moved into trash."
    }

    arguments = [
        ArgStruct(
            "-i", "--id",
            nargs="+",
            type=int,
            # required=True,
            metavar=("ID1", "ID2"),
            help="the ids of the accounts to be recovered.",
            dest="ids"
        )
    ]

    def __init__(self, **kwargs):
        super(RecoverCommand, self).__init__()
        self.ids = kwargs.get("ids", [])

    def run(self, dbhandler):
        n_recovered = 0

        if not self.ids:  # 0-len
            print("No ids given. Use --help or -h to learn about the usage.")
            return

        for i in self.ids:
            n_recovered += dbhandler.recover(i)

        print("{0} account record{1} been recovered.".format(
            "No" if n_recovered == 0 else n_recovered,
            " has" if n_recovered in (0, 1) else "s have"
        ))

        return 0
