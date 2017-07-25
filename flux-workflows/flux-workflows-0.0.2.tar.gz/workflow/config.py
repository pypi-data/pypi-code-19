import os
import click
import json
import getpass


CONFIG_FILE = os.path.expanduser("~/.cmp.json")
DEFAULT_CMP_URL = "https://portal.ntt.eu/cmp/basic/api"


class Config:
    def __init__(self, data):
        # Do we need to write the data back out to the file?
        # This is set to true if any of the option() calls
        # asked the user for input
        write = False
        self.url, write = option(
            write, data, "url",
            lambda: raw_input("CMP URL [%s]: " %
                              DEFAULT_CMP_URL) or DEFAULT_CMP_URL
        )
        self.api_key, write = option(
            write, data, "api_key",
            lambda: raw_input("CMP API key: ")
        )
        self.api_secret, write = option(
            write, data, "api_secret",
            lambda: getpass.getpass("CMP API secret: ")
        )
        self.verify_ssl, write = option(
            write, data, "verify_ssl",
            lambda: boolean_option("Verify SSL certificates", True)
        )

        if write:
            write_json_file(CONFIG_FILE, data)


def option(write, data, key, get):
    try:
        return data[key], write
    except KeyError:
        data[key] = get()
        return data[key], True


def boolean_option(desc, default=None):
    val = None

    d = "[y/n]"
    if default is True:
        d = "[Y/n]"
    elif default is False:
        d = "[y/N]"

    while val is None:
        s = raw_input("{} {}: ".format(desc, d))
        if s in ["y", "Y", "yes", "Yes", "YES"]:
            val = True
        if s in ["n", "N", "no", "No", "NO"]:
            val = False
        if s == "":
            val = default

    return val


def load():
    try:
        cfg = read_json_file(CONFIG_FILE)
        return Config(cfg)

    except ValueError as err:
        raise click.ClickException(
            "Failed to parse the CMP config file: "
            "make sure it's a valid JSON object"
        )

    except IOError as err:
        return Config({})


def write_json_file(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)
        f.write("\n")


def read_json_file(file_name):
    with open(file_name, "r") as f:
        return json.load(f)
