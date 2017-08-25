from keyman.commands.basecommand import Command
from keyman.entities import ArgStruct
from keyman.utils import edit_func


class UpdateCommand(Command):
    name = "update"

    parser_kw = {
        "help": "Update an existing account.",
        "description": "Update an existing account by editing its information."
    }

    arguments = [
        ArgStruct(
            "-i", "--id",
            type=int,
            help="the id of the account to be edited",
            dest="id"
        )
    ]

    def __init__(self, **kwargs):
        super(UpdateCommand, self).__init__()
        self.id = kwargs.get("id")

    def run(self, dbhandler):
        if not dbhandler.check_normal(self.id):
            print("No record found. Please check your id.")
            return 0

        print(
            'Editing. For each term, type "n" for "no" (using existing value),'
            ' or "y" for "yes", and then start editing the value. By default, '
            'choice "n" will be used.'
        )
        title = edit_func("Edit the title? ")
        username = edit_func("Edit your username? ")
        password = edit_func("Edit your password? ", is_passwd=True)
        description = edit_func("Edit the description? ")
        phone = edit_func("Edit phone number? ")
        email = edit_func("Edit email address? ")
        secret = edit_func("Some secret info? ", is_secret=True)

        new_values = {
            "title": title,
            "username": username,
            "password": password,
            "description": description,
            "phone": phone,
            "email": email,
            "secret": secret,
        }
        new_values = {k: v for k, v in new_values.items() if v is not None}
        # print(new_values)

        dbhandler.update(self.id, **new_values)

        print("The account has been updated.")

        return 0
