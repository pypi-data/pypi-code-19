
from timee.timee_dt import TimeeDT


class Timee(object):

    def __init__(self):
        pass

    @staticmethod
    def from_maya(maya_dt):

        """
        :type maya_dt: maya.MayaDT
        """

        _dt = maya_dt.datetime()

        timee_dt = TimeeDT(datetime_param=_dt)

        return timee_dt
