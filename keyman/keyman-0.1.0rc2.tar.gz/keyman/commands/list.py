from keyman.commands.basecommand import Command
from keyman.entities import ArgStruct


class ListCommand(Command):
    name = "list"

    parser_kw = {
        "help": "list out the accounts.",
        "description": "List out all the accounts in certain range."
    }

    arguments = [
        ArgStruct(
            "-a", "--all",
            action="store_true",
            help="show all accounts (including trash records)",
            dest="all"
        ),
        ArgStruct(
            "-t", "--trash",
            action="store_true",
            help="show all accounts in trash",
            dest="trash"
        ),
        ArgStruct(
            "-n", "--normal",
            action="store_true",
            help="show all normal accounts (no trash records will be shown)",
            dest="normal"
        ),
    ]

    def __init__(self, **kwargs):
        super(ListCommand, self).__init__()
        self.all = kwargs.get("all", False)
        self.trash = kwargs.get("trash", None)
        self.normal = kwargs.get("normal", None)

    def run(self, dbhandler):
        if self.all or self.trash and self.normal:
            _range = "a"
        elif self.trash:
            _range = "t"
        else:
            _range = "n"

        records = dbhandler.list(_range)

        print("{0} {3}record{1} found{2}.".format(
            len(records),
            "s" if len(records) >= 2 else "",
            " in trash" if _range == "t" else
            " in the whole database" if _range == "a" else "",
            "normal " if _range == "n" else ""
        ))
        print("")
        for record in records:
            print(record)

        return 0
