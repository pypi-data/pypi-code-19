import xml.etree.ElementTree as ElementTree

import requests

from utility.courseobjects import Course, Section
from utility.parse import __parse_course_string_to_url, __parse_section_string_to_url


def get_course(course: str) -> Course:
    """
    Method to get a course object from the UIUC Course Explorer API.
    Accepts a course string such as "CS 374 FA17", and returns a Course object.
    :param course: The course string to get.
    :return: The Course object created from this string.
    """
    url = __parse_course_string_to_url(course)
    try:
        return Course(__get_xml_tree(url))
    except ElementTree.ParseError:
        raise IOError("Could not find course!")


def get_section(section: str) -> Section:
    """
    Method to get a section object from the UIUC Course Explorer API.
    Accepts a section string such as "CS 374 FA17 CRN12345", and returns a Section object.
    :param section: The section string to get.
    :return: The Section object created from this string.
    """
    url = __parse_section_string_to_url(section)
    try:
        return Section(__get_xml_tree(url))
    except ElementTree.ParseError:
        raise IOError("Could not find section!")


def __get_xml_tree(url: str) -> ElementTree:
    return ElementTree.fromstring(requests.get(url).text)
