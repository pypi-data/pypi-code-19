from keyman.commands.basecommand import Command
from keyman.entities import ArgStruct


class SearchCommand(Command):
    name = "search"

    parser_kw = {
        "help": "Search for accounts.",
        "description": "Search for accounts that satisfy given conditions."
    }

    arguments = [
        ArgStruct(
            "-i", "--id",
            nargs="+",
            type=int,
            metavar=("ID1", "ID2"),
            help="search accounts by ids",
            dest="ids"
        ),
        ArgStruct(
            "-t", "--title",
            help="search accounts by title",
            dest="title"
        ),
        ArgStruct(
            "-d", "--description",
            help="search accounts by description",
            dest="desc"
        ),
        ArgStruct(
            "-a", "--show-all",
            action="store_true",
            help="show all search results (including trash)",
            dest="show_all"
        )
    ]

    def __init__(self, **kwargs):
        super(SearchCommand, self).__init__()
        self.ids = kwargs.get("ids", [])
        self.title = kwargs.get("title", None)
        self.description = kwargs.get("desc", None)
        self.show_all = kwargs.get("show_all", False)

    def run(self, dbhandler):
        records = []

        if self.ids:
            for id in self.ids:
                records.extend(dbhandler.search(self.show_all, id=id))

        else:
            records = dbhandler.search(
                self.show_all,
                title=self.title,
                description=self.description
            )

        print("{0} record{1} found.".format(
            len(records),
            "s" if len(records) >= 2 else ""
        ))
        print("")
        for record in records:
            print(record)

        return 0
