import io

from autodocumentation.compat import to_unicode


def add_prefix_to_lines(prefix, s):
    out = io.StringIO()
    for line in s.split("\n"):
        out.write(to_unicode(prefix)+to_unicode(line) + to_unicode("\n"))

    return out.getvalue()