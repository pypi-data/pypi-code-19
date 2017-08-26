import mklibpy.terminal.colored_text as colored_text
from mklibpy.util.collection import format_dict, format_list_rows

__author__ = 'Michael'


def print_vars(d):
    def __formatter(item):
        if item is None:
            item = str(item)
        return "{: >16}".format(item)

    print(format_dict(
        d,
        start="",
        end="",
        sep="\n",
        k_v=" = ",
        key_formatter=__formatter,
        val_formatter=__formatter
    ))


def print_func_names(d):
    if not d:
        return
    print(format_list_rows(
        sorted(d.keys()),
        width=16,
        columns=4,
        r=False
    ))


def print_result(text):
    print(colored_text.get_text(text, "cyan"))


def print_err(text):
    print(colored_text.get_text(text, "red"))
