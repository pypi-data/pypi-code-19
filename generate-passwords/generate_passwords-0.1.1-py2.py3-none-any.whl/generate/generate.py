def parse_commandline():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--length",
        help="The length of the password (default = %(default)s)",
        type=int,
        default=16)
    parser.add_argument(
        "--add-digits",
        help="Add digits to the password",
        action="store_true")
    parser.add_argument(
        "--add-set",
        metavar="C",
        nargs="+",
        help="Password will contain at least 1 of Cs",
        action="append",
        default=[])
    return parser.parse_args()


def main():
    import math
    import random
    import string

    options = parse_commandline()

    allowedCharacters = string.ascii_letters
    if options.add_digits:
        options.add_set.append(list(string.digits))
    if options.add_punctuation:
        options.add_set.append(list(string.punctuation))

    print("Choosing %d characters from" % (options.length))
    print("%s" % (allowedCharacters))

    if len(options.add_set) > options.length:
        raise("can not add more than %d sets" % (options.length))
    print("Password will contain at least one of the following sets:")
    for i in range(len(options.add_set)):
        s = options.add_set[i]
        print("%d: %s" % (i + 1, ", ".join(list(s))))
        allowedCharacters += "".join(s)

    print("Making %e possible passwords (%d bits)" % (
        options.length**len(allowedCharacters),
        int(math.floor(
            math.log(options.length**len(allowedCharacters)) /
            math.log(2)))))

    newPassword = ["" for i in range(options.length)]
    remaining = [i for i in range(options.length)]

    while len(remaining) > 0:
        j = remaining.pop(random.randrange(0, len(remaining)))
        if len(options.add_set) > 0:
            s = options.add_set.pop(random.randrange(0, len(options.add_set)))
            c = s[random.randrange(0, len(s))]
        else:
            c = allowedCharacters[random.randrange(0, len(allowedCharacters))]
        newPassword[j] = c

    print("password: %s" % ("".join(newPassword)))
