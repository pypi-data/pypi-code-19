
from maya import MayaDT


class TimeeDT(object):

    def __init__(self, datetime_param):
        self._datetime = datetime_param

    @property
    def datetime(self):
        """
        :rtype: datetime.datetime
        """
        return self._datetime

    @property
    def iso_string(self):

        iso_string = self.datetime.isoformat()

        return iso_string

    @property
    def basic_string(self):

        string = self.datetime.strftime('%Y-%m-%d %H:%M:%S')

        return string

    @property
    def time(self):

        string = self.datetime.strftime('%H:%M')

        return string

    def subtract(self, duration):
        # TODO

        return ''

    @property
    def maya_dt(self):

        """
        :rtype: MayaDT
        """

        maya_dt = MayaDT.from_datetime(self.datetime)

        return maya_dt

    def to_datetime(self, to_timezone, naive):

        """
        :rtype: datetime.datetime
        """

        dt = self.maya_dt.datetime(to_timezone=to_timezone, naive=naive)

        return dt

    def __repr__(self):

        repr_string = '<TimeeDT {iso_string}>'.format(
            iso_string=self.iso_string
        )

        return repr_string
