import re
import xml.etree.ElementTree as ElementTree
from datetime import datetime

import aiohttp

from utility.courseobjects import Course, Section


async def get_course(course: str) -> Course:
    """
    Asynchronous method to get a course object from the UIUC Course Explorer API.
    Accepts a course string such as "CS 374 FA17", and returns a Course object.
    :param course: The course string to get.
    :return: The Course object created from this string.
    """
    url = __parse_course_string_to_url(course)
    try:
        return Course(await __get_xml_tree(url))
    except ElementTree.ParseError:
        raise IOError("Could not find course!")


async def get_section(section: str) -> Section:
    """
    Asynchronous method to get a section object from the UIUC Course Explorer API.
    Accepts a section string such as "CS 374 FA17 CRN12345", and returns a Section object.
    :param section: The section string to get.
    :return: The Section object created from this string.
    """
    url = __parse_section_string_to_url(section)
    try:
        return Section(await __get_xml_tree(url))
    except ElementTree.ParseError:
        raise IOError("Could not find section!")


async def __get_xml_tree(url: str) -> ElementTree:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return ElementTree.fromstring(await response.text())


def __parse_course_string_to_url(course: str) -> str:
    """
    Get the URL for XML about a course, given a course string.
    Accepts a course string formatted like so:
    CS 374 FA17 CRN66445
    :param course: The course string.
    :return: The information on the course
    """
    url_format = "https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{season}/{subject}/{course}.xml?mode=cascade"
    season, year = __extract_course_time(course)
    subject, course = __extract_course_name(course)
    url = url_format.format(year=year, season=season, subject=subject, course=course)
    return url


def __parse_section_string_to_url(course: str) -> str:
    """
    Get the URL for XML about a section, given a course string.
    Accepts a course string formatted like so:
    CS 374 FA17 CRN66445
    :param course: The course string.
    :return: The information on the course
    """
    url_format = "https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{season}/{subject}/{course}/{crn}.xml"
    season, year = __extract_course_time(course)
    crn = __extract_crn(course)
    subject, course = __extract_course_name(course)
    url = url_format.format(year=year, season=season, subject=subject, course=course, crn=crn)
    return url


def __extract_course_name(course_string: str) -> (str, str):
    return re.sub("((FA|SP)[0-9]{2}|CRN[0-9]{5})", "", course_string).strip().split(" ")


def __extract_crn(course_string: str) -> str:
    res = re.search("CRN[0-9]{5}", course_string)
    crn = res.group(0)[3:]
    return crn


def __extract_course_time(course_string: str) -> (str, str):
    season_resolver = {
        1: "spring",
        2: "spring",
        3: "fall",
        4: "fall",
        5: "fall",
        6: "fall",
        7: "fall",
        8: "fall",
        9: "fall",
        10: "spring",
        11: "spring",
        12: "spring",
        "FA": "fall",
        "SP": "spring",
        "SU": "summer",
        "WN": "winter"
    }
    res = re.search("(FA|SP)[0-9][0-9]", course_string)
    if res is not None:
        time = res.group(0)
        season = season_resolver[time[0:2]]
        year = "20" + time[2:]
    else:
        season = season_resolver[datetime.now().month]
        year_offset = 1 if season == "spring" else 0
        year = str(datetime.now().year + year_offset)
    return season, year
