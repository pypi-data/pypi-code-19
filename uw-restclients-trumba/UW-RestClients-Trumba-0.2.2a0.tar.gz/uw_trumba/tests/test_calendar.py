from unittest import TestCase
from uw_trumba import get_calendar_by_name


class TestCalendarParse(TestCase):

    def test_ical_parsing(self):
        calendar = get_calendar_by_name('sea_acad-comm')
        self.assertEquals(len(calendar.walk('vevent')), 4)
