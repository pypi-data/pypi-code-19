from unittest import TestCase
from datetime import datetime
from dateutil.tz import tzutc
from uw_gradepage.grading_status import get_grading_status


class TestGradingStatus(TestCase):
    def test_get_grading_status_submitted(self):
        gs = get_grading_status(
            '2013-spring-A A-123-AA-FBB38FE46A7C11D5A4AE0004AC494FFE',
            act_as="bill")
        self.assertEquals(gs.no_grades_submitted, False)
        self.assertEquals(
            gs.section_id,
            '2013-spring-A A-123-AA-FBB38FE46A7C11D5A4AE0004AC494FFE')
        self.assertEquals(gs.display_name, 'A A 123 AA')
        self.assertEquals(gs.grading_status, None)
        self.assertEquals(gs.submitted_date,
                          datetime(2013, 6, 6, 21, 42, 19, tzinfo=tzutc()))
        self.assertEquals(gs.accepted_date,
                          datetime(2013, 6, 6, 21, 42, 20, tzinfo=tzutc()))

    def test_get_grading_status_not_submitted(self):
        gs = get_grading_status(
            '2013-spring-TRAIN-100-A-FBB38FE46A7C11D5A4AE0004AC494FFE',
            act_as="bill")
        self.assertEquals(gs.no_grades_submitted, True)
        self.assertEquals(
            gs.section_id,
            '2013-spring-TRAIN-100-A-FBB38FE46A7C11D5A4AE0004AC494FFE')
        self.assertEquals(gs.display_name, 'TRAIN 100 A')
        self.assertEquals(gs.grading_status,
                          'No submission information available')
