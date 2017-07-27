"""

"""


def import_from(module, name):
    """

    :param module:
    :param name:
    :return:
    """
    module = __import__(module, fromlist=[name])
    return getattr(module, name)


def get_main_help_string(operations_dict, update_help_str=False, doc_f=".vectortools_docstring"):
    """ Handles the main help output for Vectools

    1. The function first checks for a pre-built strings in /tmp as generating the string from scratch takes time.
    2. If pre-build string is not available it iterates over the dictionary in lib/__init__.py
    3. The first line of each doc string is read

    :return: joined_list - A string of possible operations formatted as a help string.
    """
    import os

    if not update_help_str:
        try:
            with open(os.path.abspath(os.path.dirname(__file__)) + "/" + doc_f, 'r') as doc:
                joined_list = doc.read() + "!"
        except FileNotFoundError:
            with open(doc_f, 'r') as doc:
                joined_list = doc.read() + "!"

    else:
        offset = "    "
        out_list = []
        longest_name = 0

        # Get the longest name to calculate description offset.
        for section_name in operations_dict:
            for operation_name in operations_dict[section_name]:
                if len(operation_name) > longest_name:
                    longest_name = len(operation_name)

        # Build the argparse help strings.
        for section_name in sorted(operations_dict):

            # Main types serve as headings for groups of operations.
            out_list.append(section_name)

            for operation_name in sorted(operations_dict[section_name]):

                function_path = operations_dict[section_name][operation_name]
                module_to_import = ".".join(function_path.split(".")[:-1])
                function_to_import = function_path.split(".")[-1]
                imported_function = import_from(module_to_import, function_to_import)

                # Generate the number of spaces we need to
                description_offset = "".join([" " for i in range(longest_name - len(operation_name))]) + " -"

                out_list.append("".join([
                    offset,
                    operation_name,
                    description_offset,
                    # operations_dict[section_name][operation_name].__doc__.split("\n")[0]
                    imported_function.__doc__.split("\n")[0]
                ]))

        joined_list = "\n".join(out_list)
        # Update document.
        with open(doc_f, "w") as docstring:
            docstring.write(joined_list)

    return joined_list


"""
# Saving this for later. Might be useful for auto-completion.
def get_commands(operations_dict):
    #    #if len(sys.argv) > 1 and sys.argv[1] == "--commands?":
    ops = "/tmp/.vectortools_opstring"
    if (os.path.isfile(ops)) and (os.path.getctime(ops) > os.path.getctime(__file__)):
        with open(ops, 'r') as doc:
            operations_string = doc.read()
    else:
        operations_string = ""
        for category in operations_dict:
            for operation in operations_dict[category]:
                operations_string += operation
                operations_string += " "
        with open(ops, 'w') as op:
            op.write(operations_string)
    print(operations_string)
"""