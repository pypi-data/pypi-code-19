__version__ = '0.1.1'


from aionationstates.world_ import World
world = World()


from aionationstates.nation_ import Nation
from aionationstates.nation_control import NationControl
def nation(name, *, autologin='', password=''):
    return (NationControl(name, autologin, password)
            if autologin or password else Nation(name))


from aionationstates.region_ import Region
region = Region


from aionationstates.session import set_user_agent

from aionationstates.types import (
    RateLimitError, SessionConflictError, AuthenticationError,
    NotFound, CensusScaleCurrent, CensusPoint, CensusScaleHistory,
    Dispatch, PollOption, Poll, Freedom, FreedomScores, Govt, Sectors,
    Reclassification, Reclassifications, CensusScaleChange, IssueResult,
    IssueOption, Issue, Embassies, Authority, Officer, EmbassyPostingRights,
    PostStatus, Post, Zombie, ArchivedHappening, Happening)
from aionationstates.ns_to_human import ScaleInfo, Banner

from aionationstates.utils import datetime_to_ns
