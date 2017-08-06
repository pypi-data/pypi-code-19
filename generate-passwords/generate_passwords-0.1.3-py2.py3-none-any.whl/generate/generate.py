def parse_commandline():
    import argparse
    import string

    parser = argparse.ArgumentParser(
        description="""Generates a random password from sets of characters. The
        password will contain at least one character from each set.""")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.3")
    parser.add_argument(
        "--length",
        help="The length of the password (default = %(default)s)",
        type=int,
        default=16)
    parser.add_argument(
        "--add-digits",
        help="Add the digit set (%s)" % string.digits,
        action="store_true")
    parser.add_argument(
        "--add-set",
        metavar="C",
        nargs="+",
        help="Add character C to set",
        action="append",
        default=[])
    return parser.parse_args()


def main():
    import random
    import string

    options = parse_commandline()

    password_sets = [list(string.ascii_letters)]
    if options.add_digits:
        password_sets.append(list(string.digits))
    if options.add_set:
        for item in options.add_set:
            new_set = set()
            for s in item:
                new_set = new_set | set(s)
            password_sets.append(list(new_set))

    print("Choosing %d characters from %d sets" % (options.length,
                                                   len(password_sets)))

    if len(password_sets) > options.length:
        raise("password length needs to be at least the number of sets %d" %
              (options.length))
    print("Password will contain at least one member of each of " +
          "the following sets:")

    allowedCharacters = ""
    for i in range(len(password_sets)):
        print("%d: %s" % (i + 1, ", ".join(list(password_sets[i]))))
        allowedCharacters += "".join(password_sets[i])
    allowedCharacters = "".join(set(allowedCharacters))

    newPassword = ["" for i in range(options.length)]
    remaining = [i for i in range(options.length)]

    while len(remaining) > 0:
        # We randomize where the next character is inserted into the password.
        j = remaining.pop(random.randrange(0, len(remaining)))
        if len(password_sets) > 0:
            s = password_sets.pop(random.randrange(0, len(password_sets)))
            c = s[random.randrange(0, len(s))]
        else:
            c = allowedCharacters[random.randrange(0, len(allowedCharacters))]
        newPassword[j] = c

    print("password: %s" % ("".join(newPassword)))
