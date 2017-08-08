import os
import copy
import json
import re
from six import string_types
from reactjo.helpers.data_detection import get_brackets, get_type, list_index_positions

def file_append(path, content):
    file = open(path, 'a')
    file.write('\n' + content)
    file.close()

def file_prepend(path, content):
    old_file = open(path, 'r').read()
    new_file = open(path, 'w')
    new_file.write(content + '\n')
    new_file.write(old_file)
    new_file.close()

def file_write(path, content):
    file = open(path, 'w')
    file.write(content)
    file.close()

def file_remove(path):
    os.remove(path)

def json_read(path):
    with open(path, 'r') as file:
        return json.load(file)

def json_write(path, content):
    with open(path, 'w') as file:
        json.dump(content, file, indent = 4)

def file_read(path, data = None):
    if data == None:
        return open(path, 'r').read()
    else:
        string = open(path, 'r').read()
        start  = 0
        stop   = len(string)

        for target in data:
            if isinstance(target, string_types):
                obj     = string.find(target, start)
                start   = obj
                stop    = get_brackets(string, start)['stop']
            else:
                indices = list_index_positions(string, start - 1, stop)
                obj     = indices[target]
                start   = obj
                stop    = get_brackets(string, start)['stop']

        # checks for pesky tabs, spaces, and newlines
        def before_stop(count = 1):
            c = string[stop - count]
            if c in [' ','\n','\t']:
                return before_stop(count + 1)
            else:
                return stop - count + 1

        return {
            'start': start,
            'stop': stop,
            'before_stop': before_stop(),
            'string': string[start:stop + 1]
        }

def obj_append(path, data):
    # example data:
    # data = {
    #     'target': ['config', 'more'],
    #     'content': ",\n'kittens'"
    # }
    file = file_read(path)
    target = file_read(path, data['target'])['before_stop']

    before = file[:target]
    content = data['content']
    after = file[target:]

    file_write(path, before + content + after)

def file_parse(path, data):
    string = file_read(path)
    item_starts   = [m.start() for m in re.finditer("<%", string)]
    item_ends     = [m.start() for m in re.finditer("%>", string)]
    items = []

    for n,i in enumerate(item_starts):
        start = item_starts[n]
        end   = item_ends[n] + 2
        item = string[start:end]
        key = item.strip("<%").strip("%>").strip(" ")

        items.append({'text': item, 'k': key})

    for i in items:
        string = string.replace(i['text'], data[i['k']], 1)

    return string

def file_manager(path, query, data = None):
    q = query.lower()
    if q == 'exists':
        return os.path.exists(path)
    if q in ['w', 'write', 'create']:
        file_write(path, data)
    if q in ['d','remove','delete']:
        file_remove(path)
    if q in ['p','parse','f','format']:
        return file_parse(path, data)
    if q in ['r', 'read','open']:
        if path.lower().endswith('.json'):
            return json_read(path)
        else:
            if data == None:
                return file_read(path, data)
            else:
                return file_read(path, data)['string']
    if q in ['a', 'append','add','after']:
        if isinstance(data, string_types):
            file_append(path, data)
        else:
            obj_append(path, data)