import datetime

from keyman.commands.basecommand import Command
from keyman.utils import input_func
from keyman.entities import Account


class InsertCommand(Command):
    name = 'insert'

    parser_kw = {
        "help": "Insert a new account.",
        "description": "Insert an account into the database."
    }

    noargs_for_help = False

    def run(self, dbhandler):
        print('Insert a new account. Fields marked with a "*" is required.')

        title = input_func("(*) Enter the title: ", required=True)
        username = input_func("Enter your username: ")
        password = input_func("", is_passwd=True)
        description = input_func("Description about the account: ")
        phone = input_func("Phone number: ")
        email = input_func("Email address: ")
        secret = input_func("Some secret info: ", is_secret=True)

        create_time = datetime.datetime.now()

        new_account = Account(
            id=None,
            title=title,
            username=username,
            description=description,
            password=password,
            phone=phone,
            email=email,
            secret=secret,
            deleted=0,
            create_date=create_time,
            last_update=create_time
        )

        dbhandler.insert(new_account)

        print("A new account has been added.")

        return 0
