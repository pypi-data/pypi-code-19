import dpath

from Utils import try_get_value_from_dictionary, flatten_value, decode_json
from Utils.TextFunctions import sort_strings_by_length

path_separator = '|||'


def fix_primary_values(value, jentity, path=[]):
    """

    :param value:
    :param jentity:
    :param path:
    :return:
    """
    if isinstance(value, dict):
        for key in value:
            field_value = decode_json(try_get_value_from_dictionary(jentity, path + [key]))
            if key in ['alternative']:
                if len(field_value) == 1 and isinstance(field_value[0], list) and len(field_value[0]) == 1:
                    dpath.util.delete(jentity, "/".join(path + [key]))
                    dpath.util.new(jentity, path="/".join(path + [key]), value=field_value[0])
            elif key in ['primary']:
                if len(field_value) == 1 and isinstance(field_value, list):
                    dpath.util.delete(jentity, "/".join(path + [key]))
                    dpath.util.new(jentity, path="/".join(path + [key]), value=field_value[0])
            elif key in ['fname', 'lname', 'groups']:
                if len(field_value) == 1 and isinstance(field_value, list):
                    dpath.util.delete(jentity, "/".join(path + [key]))
                    dpath.util.new(jentity, path="/".join(path + [key]), value=field_value[0])
            elif key in ['education', 'experience']:
                if not isinstance(field_value, list):
                    dpath.util.delete(jentity, "/".join(path + [key]))
                    dpath.util.new(jentity, path="/".join(path + [key]), value=[field_value])
            else:
                fix_primary_values(value[key], jentity, path + [key])


def convert_dictionary_to_path_list(jentity, path):
    """

    :param path:
    :param jentity:
    :return:
    """
    for key, value in sorted(jentity.items(), key=lambda x: x[0]):
        if isinstance(value, dict) and key not in ['experience', 'education', 'location']:
            for r in convert_dictionary_to_path_list(value, path + [key]):
                yield r
        else:
            yield path_separator.join(path + [key]), value

def group_paths(paths):
    """
    Groups same paths to a dictionary with path as a key and all the values in a list as a value
    :param paths:
    :return: dictionary with grouped paths
    """
    grouped_paths = {}
    for path in paths:
        parts = path.split(path_separator)
        value = parts[-1]
        path_core = path_separator.join(parts[:-1])

        if path_core not in grouped_paths:
            grouped_paths[path_core] = value

        if value != grouped_paths[path_core]:
            if type(grouped_paths[path_core]) is not list:
                grouped_paths[path_core] = [grouped_paths[path_core]]
            grouped_paths[path_core].append(value)
        else:
            continue

    return grouped_paths


def fix_urls(urls):
    """
    Removes URLs that are supersets of others (specifically, LinkedIn URLs)
    :param urls:
    :return:
    """
    urls = map(lambda x: x.replace('http://', '').replace('https://', ''), urls)
    urls = filter(lambda x: not isinstance(x, list), urls)
    urls = sorted(urls, sort_strings_by_length)

    result = []
    ignored_urls = []

    for url in urls:
        subsets = filter(lambda x: url in x, urls)
        if min(subsets) not in result and min(subsets) not in ignored_urls:
            result.append(min(subsets))
        if len(subsets) > 1:
            ignored_urls.extend([item for item in subsets if item != min(subsets)])

    return result


def compare_jentity_values(old_value, new_value):
    """

    :param old_value:
    :param new_value:
    :return:
    """
    if len(old_value) == 0 and len(new_value) == 0:
        return True
    elif old_value == new_value:
        return True
    else:
        return False


def harmonize_data_type(v1, v2):
    """

    :param v1:
    :param v2:
    :return:
    """
    if not isinstance(v1, list):
        v1 = [v1]
    else:
        v2 = [v2]

    return v1, v2



def fix_nulls_in_dictionary(jentity):
    """

    :param jentity:
    :return:
    """
    if type(jentity) == list:
        return filter(lambda x: x is not None, jentity)

    if type(jentity) is dict:
        for key in jentity.keys():
            if jentity[key] is None:
                del jentity[key]

            if type(jentity) is dict:
                jentity[key] = fix_nulls_in_dictionary(jentity[key])

    return jentity


def identify_list_fields(value, jentity, path=[], items=[]):
    """

    :param value:
    :param jentity:
    :param path:
    :return:
    """
    if isinstance(value, dict):
        for key in value.keys():
            field_value = try_get_value_from_dictionary(jentity, path + [key])

            if isinstance(field_value, dict):
                identify_list_fields(value[key], jentity, path + [key], items)

            if isinstance(field_value, list):
                items.append((path + [key], field_value))

    return items


def fix_list_fields(jentity):
    """

    :param jentity:
    :return:
    """
    list_fields = identify_list_fields(jentity, jentity)
    non_array_fields = ['fname', 'lname', 'location', 'position', 'company', 'primary', 'picture']
    for path, value in list_fields:
        path = '/'.join(path)
        value = flatten_value(value)

        if len(dpath.util.search(jentity, path)) > 0:
            dpath.util.delete(jentity, path)

        if any(f in path  for f in non_array_fields):
            dpath.util.new(jentity, path, value=value)
        elif not isinstance(value, list):
            dpath.util.new(jentity, path, value=[value])
        else:
            dpath.util.new(jentity, path, value=value)

    return jentity