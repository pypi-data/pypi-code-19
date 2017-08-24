from keyman.commands.insert import InsertCommand
from keyman.commands.remove import RemoveCommand
from keyman.commands.recover import RecoverCommand
from keyman.commands.search import SearchCommand
from keyman.commands.list import ListCommand
from keyman.commands.update import UpdateCommand

commands_order = [
    InsertCommand,
    RemoveCommand,
    RecoverCommand,
    SearchCommand,
    ListCommand,
    UpdateCommand
]

commands_dict = {c.name: c for c in commands_order}
