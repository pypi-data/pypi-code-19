import datetime
from unittest import TestCase
from restclients_core.exceptions import DataFailureException
from uw_grad.leave import get_leave_by_regid
from uw_pws.util import fdao_pws_override
from uw_grad.util import fdao_grad_override


@fdao_grad_override
@fdao_pws_override
class LeaveTest(TestCase):

    def test_get_leave_by_regid(self):
        requests = get_leave_by_regid(
            "9136CCB8F66711D5BE060004AC494FFE")

        self.assertEqual(len(requests), 5)
        leave = requests[0]
        self.assertIsNotNone(leave.json_data())
        self.assertEqual(leave.reason,
                         "Dissertation/Thesis research/writing")
        self.assertEqual(leave.submit_date,
                         datetime.datetime(2012, 9, 10, 9, 40, 3, 360000))
        self.assertEqual(leave.status, "paid")
        self.assertTrue(leave.is_status_paid())
        self.assertFalse(leave.is_status_approved())
        self.assertFalse(leave.is_status_denied())
        self.assertFalse(leave.is_status_requested())
        self.assertFalse(leave.is_status_withdrawn())
        self.assertEqual(len(leave.terms), 1)
        self.assertEqual(leave.terms[0].quarter, "autumn")
        self.assertEqual(leave.terms[0].year, 2012)

    def test_error(self):
        self.assertRaises(DataFailureException,
                          get_leave_by_regid,
                          "00000000000000000000000000000001")
