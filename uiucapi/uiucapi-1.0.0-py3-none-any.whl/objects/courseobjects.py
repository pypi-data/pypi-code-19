from datetime import datetime
from typing import List
from xml.etree.ElementTree import Element


class GenedCategory:
    def __init__(self, xml_root: Element):
        self.__type = xml_root.attrib['id']
        self.__description = xml_root.find("./description").text.strip()


class Section:
    def __init__(self, xml_root: Element):
        self.__crn = int(xml_root.attrib['id'])
        self.__section_number = xml_root.find("./sectionNumber").text.strip()
        self.__enrollment_status = xml_root.find("./enrollmentStatus").text
        self.__start_date = datetime.strptime(xml_root.find("./startDate").text, "%Y-%m-%d-%H:%M")
        self.__end_date = datetime.strptime(xml_root.find("./endDate").text, "%Y-%m-%d-%H:%M")

    @property
    def crn(self) -> int:
        return self.__crn

    @property
    def section_number(self) -> str:
        return self.__section_number

    @property
    def registration_status(self) -> str:
        return self.__enrollment_status

    @property
    def start_date(self) -> datetime:
        return self.__start_date

    @property
    def end_date(self) -> datetime:
        return self.__end_date


class Course:
    def __init__(self, xml_root: Element):
        self.__subject, self.__number = xml_root.attrib['id'].split()
        self.__label = xml_root.find("./label").text
        self.__description = xml_root.find("./description").text.strip()
        self.__credit_hours = int(xml_root.find("./creditHours").text.split()[0])
        self.__gened_categories = [GenedCategory(x) for x in xml_root.findall("./genEdCategories/*")]
        self.__sections = [Section(x) for x in xml_root.findall("./detailedSections/*")]
        self.__year = int(xml_root.find("./parents/calendarYear").attrib['id'])
        self.__season = int(xml_root.find("./parents/calendarYear").text.split()[0])

    @property
    def subject(self) -> str:
        return self.__subject

    @property
    def name(self) -> str:
        return self.__label

    @property
    def description(self) -> str:
        return self.__description

    @property
    def credit_hours(self) -> int:
        return self.__credit_hours

    @property
    def gened_categories(self) -> List[GenedCategory]:
        return self.__gened_categories

    @property
    def sections(self) -> List[Section]:
        return self.__sections
