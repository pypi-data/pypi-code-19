from io import BytesIO
from collections import defaultdict, OrderedDict

from lxml import etree


class Stack:
    def __init__(self):
        self._storage = []

    def push(self, item):
        self._storage.append(item)

    def pop(self):
        return self._storage.pop()

    def peek(self):
        return self._storage[-1]


def process_element_text(text):
    # xmltodict compatibility: strip whitespace
    # and transform empty strings to None values
    return text.strip() or None \
        if text is not None \
        else None


def add_data_to_parent(tag, data, parent):
    """
    Add an item of data associated with a given XML tag to its parent.
    If the key already exists in the parent,
    the key will be transformed into a list and the data appended to it


    :param tag: The XML element tag associated with the data being inserted
    :param data: The data being added to the parent dictionary
    :param parent: The dictionary to inject data into
    """
    if tag in parent:
        existing_elem = parent[tag]
        if not isinstance(existing_elem, list):
            parent[tag] = [existing_elem]
        parent[tag].append(data)
    else:
        parent[tag] = data


def parse(xml, dict_factory=OrderedDict):
    """
    Convert a raw XML string into a Python dictionary.
    This function is designed to be compatible with
    the default behaviour of ``xmltodict.parse``,
    and should act as a drop-in replacement

    :param xml: A raw XML string to be parsed.
    :param dict_factory: Specifies what dictionary type should be used
                            for building the return value.
                            By default, ``OrderedDict`` is used to mimic
                            the behaviour of ``xmltodict``.
    :return: A dictionary containing the data from the XML string,
                using each element's name as the dictionary key.
                Elements with nested children or attributes are dictionaries,
                while plain-text elements are strings.
    """

    # Prepares a generator to iteratively step through the XML tree structure
    # to avoid incurring the memory overhead of loading the full XML tree
    # Only open/close tag events are required for preparing the dict
    xml_iter = etree.iterparse(
        BytesIO(xml.encode('utf-8')),
        events=('start', 'end'))

    depth = 0
    depth_dict = defaultdict(dict_factory)
    for action, element in xml_iter:
        attributes = element.attrib

        if action == 'start':
            depth += 1
            # xmltodict compatibility: attributes added first
            if attributes:
                curr_node = depth_dict[depth]
                for attr_key, attr_value in attributes.items():
                    curr_node['@' + attr_key] = attr_value
        elif action == 'end':
            new_depth = depth - 1
            parent = depth_dict[new_depth]
            has_children = len(element)
            if has_children or attributes:
                curr_node = depth_dict.pop(depth)
                value = process_element_text(element.text)
                # xmltodict compatibility: None values are not added
                # to elements that have attributes
                if attributes and value is not None:
                    curr_node['#text'] = value
                add_data_to_parent(element.tag, curr_node, parent)
            else:
                value = process_element_text(element.text)
                add_data_to_parent(element.tag, value, parent)
            depth = new_depth
            # Clear the data associated with the Element
            # e.g. nested elements, text context
            # once it has been consumed
            element.clear()
    return depth_dict[0]
