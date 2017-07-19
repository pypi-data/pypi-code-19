import re

regx = re.compile('(\d+)')


def natural_key(item):
    return [int(part) if part.isdigit() else part for part in regx.split(item)]
