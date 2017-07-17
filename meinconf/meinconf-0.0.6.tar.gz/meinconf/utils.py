import importlib
import re
from contextlib import contextmanager


@contextmanager
def ok(*exceptions):
    """Context manager to pass exceptions.

    :param exceptions: Exceptions to pass
    """
    try:
        yield
    except Exception as e:
        if isinstance(e, exceptions):
            pass
        else:
            raise e


# From honcho
def honcho_parse_env(content):
    values = {}
    for line in content.splitlines():
        m1 = re.match(r'\A([A-Za-z_0-9]+)=(.*)\Z', line)
        if m1:
            key, val = m1.group(1), m1.group(2)

            m2 = re.match(r"\A'(.*)'\Z", val)
            if m2:
                val = m2.group(1)

            m3 = re.match(r'\A"(.*)"\Z', val)
            if m3:
                val = re.sub(r'\\(.)', r'\1', m3.group(1))

            values[key] = val
    return values


def import_string(name):
    return importlib.import_module(name)
