# Copyright (c) 2017 David Sorokin <david.sorokin@gmail.com>
#
# Licensed under BSD3. See the LICENSE.txt file in the root of this distribution.

def encode_str(str):
    """Encode the string."""
    str = str.replace('\r\n', ' ')
    str = str.replace('\n', ' ')
    str = str.replace('\r', ' ')
    str = str.replace('\\', '\\\\')
    str = str.replace('"', '\\"')
    str = '"' + str + '"'
    return str

def encode_maybe(encode_func, value):
    """Encode the value."""
    if value is None:
        return 'Nothing'
    else:
        return '(Just $ ' + encode_func(value) + ')'

def write_list(write_item_using_indent, collection, file, indent):
    """Write the collection in the file."""
    file.write('[')
    indent = indent + ' '
    first = True
    for item in collection:
        if first:
            first = False
            write_item_using_indent(file, item, indent)
        else:
            file.write(',\n')
            file.write(indent)
            write_item_using_indent(file, item, indent)
    file.write(']')

def write_record_fields(write_item_using_indent_dict, file, indent):
    """Write the records fields in the file."""
    first = True
    for name in write_item_using_indent_dict:
        func = write_item_using_indent_dict[name]
        if first:
            first = False
            file.write(' {\n')
            file.write(indent)
        else:
            file.write(',\n')
            file.write(indent)
        file.write(name)
        file.write(' = ')
        func(file, indent)
    if not first:
        file.write(' }')

def write_mconcat(write_item_using_indent, collection, file, indent):
    """Write the monoid concatination in the file."""
    first = True
    for item in collection:
        if first:
            first = False
            file.write('(')
            write_item_using_indent(file, item, indent)
            file.write(')')
        else:
            file.write(' <>\n')
            file.write(indent)
            file.write('(')
            write_item_using_indent(file, item, indent)
            file.write(')')

def write_sources(sources, file, indent):
    """Write the result sources in the file."""
    func = lambda file, item, indent: file.write(item.read_results())
    write_mconcat(func, sources, file, indent)
