from calendar import monthrange
import datetime
import pandas


class CalendarDiscovery(object):
    def __init__(self, date):
        self.date = self.set_date(date)

    def __months_by_quarter(self, quarter):
        """A quarter is based on the index of the list.  Q1 is quarters[0].
        Each index contains a list of 3 values which donate a numeric value
        of the months.

        returns list of the months int for that quarter
        """
        quarters = [
                [1,2,3],
                [4,5,6],
                [7,8,9],
                [10,11,12]
                ]
        return quarters[quarter]

    def __days(self):
        self.days = self.get_days()

    def __quarter(self):
        self.quarter = self.get_quarter()

    def __day(self):
        self.day = self.get_day()

    def __month(self):
        self.month = self.get_month()

    def __year(self):
        self.year = self.get_year()

    def set_date(self,date=None):
        if date is None:
            self.date = datetime.datetime.now()
        self.date = date
        self.__day()
        self.__days()
        self.__quarter()
        self.__month()
        self.__year()
        return self.date

    def get_day(self):
        return self.date.day

    def get_days(self):
        return self.get_days_in_month(self.date.month,self.date.year)

    def get_month(self):
        return self.date.month

    def get_year(self):
        return self.date.year

    def get_quarter(self):
        return pandas.Timestamp(self.date).quarter

    def get_months_in_quarter(self, quarter=None):
        if not quarter:
            quarter = self.quarter
        return self.__months_by_quarter(quarter - 1)

    def get_days_in_month(self, month, year):
        return monthrange(year,month)[1]

    def get_days_of_month_for_quarter(self, quarter=None):
        if not quarter:
            quarter = self.quarter
        months = self.get_months_in_quarter()
        days_in_month_for_quarter = []
        for month in months:
            days_in_month_for_quarter.append(self.get_days_in_month(month,self.year))
        return days_in_month_for_quarter
