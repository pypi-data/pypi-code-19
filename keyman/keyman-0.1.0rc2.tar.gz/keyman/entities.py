from keyman.utils import tstmp2dt
from keyman.utils import CBCCipher
from keyman.config import KEY, IV


# TODO: add support for add_mutually_exclusive_group?
class ArgStruct:
    """
    The struct containing all parameters that are needed by
    argparse.ArgumentParser.add_argument().

    """

    # Either a name or a list of option strings, e.g. foo or -f, --foo.
    names = None

    keys = [
        # The basic type of action to be taken when this argument is encountered
        # at the command line.
        "action",

        # The number of command-line arguments that should be consumed.
        "nargs",

        # A constant value required by some action and nargs selections.
        "const",

        # The value produced if the argument is absent from the command line.
        "default",

        # The type to which the command-line argument should be converted.
        "type",

        # A container of the allowable values for the argument.
        "choices",

        # Whether or not the command-line option may be omitted (optionals only).
        "required",

        # A brief description of what the argument does.
        "help",

        # A name for the argument in usage messages.
        "metavar",

        # The name of the attribute to be added to the object returned by
        # parse_args().
        "dest"
    ]

    def __init__(self, *args, **kwargs):
        self.names = args
        for k, v in kwargs.items():
            if k in self.keys:
                setattr(self, k, v)

    def get_kwargs(self):
        return {k: getattr(self, k) for k in self.keys
                if hasattr(self, k)}


class Account:
    """
    The class describing the data structure of an account.

    _data is a dict used to store all the data. Values of id, deleted,
    create_date and last_update are set/changed in DBHandler automatically.

    """

    # the order of this list corresponds to the creation order of table ACCOUNT;
    # see keyman.handler.confighandler.init_local_dir()
    keys = [
        "id",
        "title",
        "username",
        "description",
        "password",  # the encrypted data
        "phone",
        "email",
        "secret",
        "deleted",
        "create_date",
        "last_update",
    ]

    def __init__(self, **data):
        self._data = {}
        for k in self.keys:
            if k in data:
                self._data[k] = data.pop(k)
            else:
                self._data[k] = None

        if data:
            print(
                "Some items are not supported by out database currently.\n"
                "The following settings will be ignored:\n"
                "{0}".format(data)
            )

    # @property
    def items(self):
        """ Generate all data items. """
        return list(self._data.items())

    # @property
    def values(self):
        """
        Generate all data values.

        Note that in order to make the values in the list returned by this
        function are ordered by keys in self.keys, list comprehension is used.

        """
        # return list(self._data.values())
        return [self._data[k] for k in self.keys]

    def keystr(self):
        """ Generate the string of the names of data terms. """
        _keystr = ""
        for k in self.keys:
            _keystr += k + ", "
        return _keystr[:-2]

    def get(self, key):
        """ Get the value of a certain term. """
        return self._data[key]

    def set(self, key, value):
        """ Set the value of a certain term. """
        if key in self._data.keys():
            self._data[key] = value
            return True  # succeed
        else:
            return False  # fail

    def __str__(self):
        strings = []
        for k in self.keys:
            if k == "deleted":
                if int(self._data[k]) == 1:
                    strings[0] += " (removed)"
            elif k in ("password", "secret"):
                strings.append(
                    k + ": " +
                    (CBCCipher(KEY, IV).decrypt(eval(self._data[k]))
                     if self._data[k] != "" else "")
                )
            elif k not in ("create_date", "last_update"):
                strings.append(k + ": " + str(self._data[k]))
            else:
                strings.append(k + ": " + str(tstmp2dt(self._data[k])))
        return "\n".join(strings) + "\n"


if __name__ == "__main__":
    print(Account.keys)
    print(Account(
        id="id",
        title="title",
        username="username",
        description="description",
        password="password",
        phone="phone",
        email="email",
        secret="secret",
        deleted="deleted",
        create_date="create_date",
        last_update="last_update",
    ).values())
    print(Account(username="pass", password="password"))
    Account(username="pass", password="password", phone="123")
