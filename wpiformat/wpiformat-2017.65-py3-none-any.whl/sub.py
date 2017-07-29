"""This task performs find-replace actions with regular expressions."""

import re

from . import task


class Sub(task.Task):

    def get_file_extensions(self):
        return task.get_config("cExtensions") + \
            task.get_config("cppHeaderExtensions") + \
            task.get_config("cppSrcExtensions") + \
            task.get_config("otherExtensions")

    def run(self, name, lines):
        linesep = task.get_linesep(lines)

        file_changed = False
        output = ""

        regexes = [
            re.compile(
                "virtual([ ]+"  # "virtual" keyword
                "\w+[ ]+"  # Return type
                "\w+[ ]*"  # Function name
                "\([a-zA-Z0-9_, ]*\)[ ]+"  # Function arguments
                ")override"  # "override" keyword
                ,
                re.X)
        ]

        for line in lines.splitlines():
            for regex in regexes:
                out = regex.sub("\g<1>override", line)
                if line != out:
                    file_changed = True
                output += out + linesep

        return (output, file_changed, True)
