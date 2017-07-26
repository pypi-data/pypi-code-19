import csv
import gzip
import os
import glob
import re
from collections import defaultdict

from fnmatch import fnmatch
from os.path import join, isfile, dirname

from configobj import ConfigObj

from bgparsers import readers

ANNOTATION_FILE_EXTENSION = "bginfo"


def __null_value(value):
    return None if value == "" else value


def __read_annotations(annotation_file):

    info = ConfigObj(annotation_file)

    extensions = info['pattern'] if isinstance(info['pattern'], list) else [info['pattern'].strip()]
    recursive = info.get('recursive', 'false').lower() in ["true", "yes", "y", "1", "ok"]
    annotations = info['annotations']

    for k in annotations.keys():
        v = annotations[k]
        if isinstance(v, str) and v.startswith('(') and v.endswith(')'):
            annotate = eval(v)
            if annotate[0] == 'mapping':
                mapping_files = join(dirname(annotation_file), annotate[2])
                values = {}
                for mapping_file in glob.glob(mapping_files):
                    open_method = gzip.open if mapping_file.endswith('gz') else open
                    with open_method(mapping_file, "rt") as fd:
                        for r in csv.DictReader(fd, delimiter='\t'):
                            a, b = __null_value(r[annotate[3]]), __null_value(r[annotate[4]])
                            if a is not None and b is not None:
                                if len(annotate) > 5:
                                    b = annotate[5](b)
                                values[a] = b
                annotations[k] = ('mapping', annotate[1], values)
            if annotate[0] == 'filename':
                annotations[k] = ('filename', re.compile(annotate[1]), (lambda v: v) if len(annotate) == 2 else annotate[2])
            if annotate[0] == 'internal':
                annotations[k] = ('internal', annotate[1])


    return recursive, {e: annotations for e in extensions}


def __merge_annotations(a, b):
    """

    :param a: The first annotations dictionary
    :param b: The second annotations dictionary. This annotations have preference and will override A annotations if there is a conflict
    :return: The union of A and B annotation dictionaries
    """

    # Clone A
    c = {k: dict(v) for k, v in a.items()}

    # Update or add B entries
    for k, v in b.items():
        if k in c:

            # Update the annotations
            for kv, vv in v.items():
                if kv not in c[k]:
                    c[k][kv] = vv
                else:
                    if isinstance(c[k][kv], list):
                        # If it's a list concat them instead of override it
                        vv_list = vv if isinstance(vv, list) else [vv]
                        c[k][kv] = list(c[k][kv]) + vv_list
                    else:
                        # Override the value
                        c[k][kv] = vv

        else:
            c[k] = dict(v)

    return c


def __where_cmp(data_value, where_value):
    if isinstance(where_value, list) or isinstance(where_value, set):
        return data_value in where_value
    else:
        return data_value != where_value


def __where_match(annotations, where=None):

    if where is None:
        return True

    for k, v in where.items():
        if k in annotations:
            value = annotations[k]
            if isinstance(value, list):
                if v not in value:
                    return False
            elif isinstance(value, tuple) and value[0] == 'mapping':
                if isinstance(v, list) or isinstance(v, set):
                    filtered_mapping = {mk: mv for mk, mv in value[2].items() if mv in v}
                    annotations[k] = ('filtering', value[1], filtered_mapping)
                    if len(filtered_mapping) == 0:
                        return False
                else:
                    where_valid_values = set([nk for nk, nv in value[2].items() if nv == v])
                    annotations[k] = (value[1], v, where_valid_values)
                    if len(where_valid_values) == 0:
                        return False
            else:
                if not __where_cmp(value, v):
                    return False
        else:
            return False

    return True


def __process_annotations(annotations, filename):
    for k in annotations:
        value = annotations[k]
        if isinstance(value, tuple) and value[0] == 'filename':
            m = value[1].match(filename)
            annotations[k] = None
            if m is not None:
                g = m.groups()
                annotations[k] = value[2](*g)

    return annotations


def find(basepath, where=None, annotations=None):

    global_annotations = {} if annotations is None else annotations

    # Annotations that only apply to the current folder level
    local_annotations = {}

    # Update annotations
    for annotation_file in glob.iglob(join(basepath, "*.{}".format(ANNOTATION_FILE_EXTENSION))):
        recursive, ann = __read_annotations(annotation_file)

        # Update global annotations
        if recursive:
            global_annotations = __merge_annotations(global_annotations, ann)
        else:
            local_annotations = __merge_annotations(local_annotations, ann)

    # Merge local and global annotations, but local have preference over global
    local_annotations = __merge_annotations(global_annotations, local_annotations)

    # Find files
    for file in os.listdir(basepath):
        file_path = join(basepath, file)

        if isfile(file_path):
            file_annotations = {}
            pattern_matches = 0
            for pattern, annotations in local_annotations.items():
                if fnmatch(file_path, pattern):
                    pattern_matches += 1
                    file_annotations.update(annotations)

            # Process filename annotations
            file_annotations = __process_annotations(file_annotations, file)

            if pattern_matches > 0 and __where_match(file_annotations, where=where):
                yield file_path, file_annotations

        else:
            # Search subfolders
            for f, a in find(file_path, where=where, annotations=global_annotations):
                yield f, a


def __get_unique_values(file, key):
    values = set()
    for r in readers.variants(file):
        values.add(r[key])
    return values


def get_samples_ids(file):
    return __get_unique_values(file, 'SAMPLE')


def get_donor_ids(file):
    return __get_unique_values(file, 'DONOR')


def groupby(basepath, by=None, where=None, no_group_by=True):
    assert by != None, "You must provide a 'by' annotation"

    results = defaultdict(list)

    for f, a in find(basepath, where=where):
        by_value = a.get(by, None)

        if no_group_by:
            if by_value is None or isinstance(by_value, tuple):
                a_clone = dict(a)
                a_clone[by] = ('not', by_value)
                results[None].append((f, a_clone))

        if by_value is None:
            continue

        if isinstance(by_value, tuple):

            if by_value[0] == 'internal':
                values = by_value[1]
                if not isinstance(values, set):
                    if values == 'SAMPLE':
                        values = get_samples_ids(f)
                        a[by] = ('internal', values)
                    elif values == 'DONOR':
                        values = get_donor_ids(f)
                        a[by] = ('internal', values)
                    else:
                        raise NotImplementedError("'{}' internal annotation not implemented".format(values))

                for s in values:
                    a_clone = dict(a)
                    a_clone[by] = (by, s, {s})
                    results[s].append((f, a_clone))

            elif isinstance(by_value[2], dict):
                inv_dict = {}
                for k, v in by_value[2].items():
                    inv_dict[v] = inv_dict.get(v, set())
                    inv_dict[v].add(k)

                for k, values in inv_dict.items():
                    a_clone = dict(a)
                    a_clone[by] = (by_value[1], k, values)
                    results[k].append((f, a_clone))
            else:
                results[by_value[1]].append((f, a))

        else:
            results[by_value].append((f, a))

    for key, group in results.items():
        yield key, group

















