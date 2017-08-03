"""
This file contains basic tests for the core app.
"""

from django.core.urlresolvers import reverse
from django.utils import timezone

from .models import ExpenseItem, ExpenseCategory, RevenueItem, RevenueCategory
from .constants import getConstant
from .utils.tests import DefaultSchoolTestCase


class RevenueTest(DefaultSchoolTestCase):

    def test_revenuesubmission(self):
        """
        Tests that we can log in as a superuser and add a class series
        from the admin form, and that that class shows up on the
        registration page.
        """

        # First, check that the registration page loads, and that there
        # are no open or closed series on the registration page.
        '''

        response = self.client.get(reverse('registration'))
        self.assertEqual(response.status_code,200)
        self.assertQuerysetEqual(response.context['regOpenSeries'], [])
        self.assertQuerysetEqual(response.context['regClosedSeries'], [])

        # Check that the Add a class series page loads for the superuser
        self.client.login(username=self.superuser.username,password='pass')
        add_series_response = self.client.get(reverse('admin:core_series_add'))
        self.assertEqual(add_series_response.status_code,200)
        self.client.logout()
		'''
		pass

	def test_registration_creates_revenue(self):
		"""
		Process a registration with a cash payment and ensure that an
		associated RevenueItem is created that links to the Registration's
		Invoice.
		"""
		pass

class ExpensesTest(DefaultSchoolTestCase):

	def test_expensesubmission(self):
		"""
		Tests that we can log in as a superuser and add an ExpenseItem
		using the Expense submission form.
		"""
		pass

	def test_event_creates_teachingexpense(self):
		"""
		"""
		pass

	def test_event_creates_venueexpense(self):
		"""
		Test that venue expenses are reported for
		"""

	def test_substitute_creates_expense(self):
		"""
		Report a substitute teacher for a class that has ended and ensure
		that an ExpenseItem associated with that substitute teacher is
		created, and that the existing ExpenseItem associated with the
		existing teacher is updated appropriately
		"""
		pass


class FinancialSummariesTest(DefaultSchoolTestCase):

    def test_annual_detailview(self):
    	pass

    def test_monthly_detailview(self):
    	pass

    def test_summary_bymonth(self):
    	pass

    def test_summary_byevent(self):
    	pass

