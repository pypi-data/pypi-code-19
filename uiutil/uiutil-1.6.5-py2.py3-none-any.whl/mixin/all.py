
from var import VarMixIn
from poll import PollMixIn
from style import StyleMixIn
from widget import WidgetMixIn
from layout import FrameLayoutMixIn
from classutils.observer import ObserverMixIn


class AllMixIn(FrameLayoutMixIn,
               StyleMixIn,
               WidgetMixIn,
               VarMixIn,
               PollMixIn,
               ObserverMixIn):

    def __init__(self,
                 *args,
                 **kwargs):

        super(AllMixIn, self).__init__(*args, **kwargs)
