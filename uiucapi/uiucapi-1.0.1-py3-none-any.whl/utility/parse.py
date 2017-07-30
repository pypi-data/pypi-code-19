import re
from datetime import datetime


def __parse_course_string_to_url(course: str) -> str:
    """
    Get the URL for XML about a course, given a course string.
    Accepts a course string formatted like so:
    CS 374 FA17 CRN66445
    :param course: The course string.
    :return: The information on the course
    """
    url_format = "https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{season}/{subject}/{course}.xml?mode=cascade"
    season, year, *_ = __extract_course_time(course)
    subject, course, *_ = __extract_course_name(course)
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
    season, year, *_ = __extract_course_time(course)
    crn = __extract_crn(course)
    subject, course, *_ = __extract_course_name(course)
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
