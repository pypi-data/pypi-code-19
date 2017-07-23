# TODO slots
# TODO split into submodules?

import html
from contextlib import suppress
from typing import NamedTuple
from enum import Flag, Enum, auto
from functools import reduce, total_ordering
from operator import or_
# Needed for type annotations
import datetime
from typing import List, Optional, Awaitable
from aionationstates.ns_to_human import Banner, ScaleInfo

from aionationstates.utils import timestamp, banner_url, unscramble_encoding
from aionationstates.ns_to_human import banner, census_info


class RateLimitError(Exception):
    pass


class SessionConflictError(Exception):
    pass


class AuthenticationError(Exception):
    pass


class NotFound(Exception):
    pass


class CensusScaleCurrent:
    """World Census scale data about a nation.

    .. warning::

        With the exception of score, you must not expect the fields
        to update instantly.

        For the exact same reason of NationStates' excessive
        quirkiness, those fields may be missing (set to ``None``) on
        newly-founded nations (perhaps also in other cases, there is
        not a way to reliably test).  You will need to account for
        that in your code.

    Attributes:
        info: Static information about the scale.
        score: The absolute census score.  All the other scale values
            are calculated (by NationStates) from scale scores of
            multiple nations.  Should always be there if you request
            it.
        rank: World rank by the scale.
        prank: Percentage World rank by the scale.
        rrank: Regional rank by the scale.
        prrank: Percentage Regional rank by the scale.
    """
    info: ScaleInfo
    score: float
    rank: Optional[int]
    prank: Optional[float]
    rrank: Optional[int]
    prrank: Optional[float]

    def __init__(self, elem):
        self.info = census_info[int(elem.get('id'))]
        self.score = float(elem.find('SCORE').text)
        # For recently-founded nations (and maybe in other cases as well, who
        # knows) the ranks & percentages may not show up even if requested.
        self.rank = self.prank = self.rrank = self.prrank = None
        with suppress(AttributeError, TypeError):
            self.rank = int(elem.find('RANK').text)
        with suppress(AttributeError, TypeError):
            self.prank = float(elem.find('PRANK').text)
        with suppress(AttributeError, TypeError):
            self.rrank = int(elem.find('RRANK').text)
        with suppress(AttributeError, TypeError):
            self.prrank = float(elem.find('PRRANK').text)

    def __repr__(self):
        return f'<CensusScaleCurrent #{self.info.id} {self.info.title}>'


class CensusPoint(NamedTuple):
    """What the scale score was on a particular date.

    Attributes:
        timestamp: When the score was recorded.
        score: What it was.
    """
    timestamp: datetime.datetime
    score: float


class CensusScaleHistory:
    """Change of a World Census scale score of a nation through time.

    Attributes:
        info: Static information about the scale.
        history: The data itself.
    """
    info: ScaleInfo
    history: List[CensusPoint]

    def __init__(self, elem):
        self.info = census_info[int(elem.get('id'))]
        self.history = [
            CensusPoint(
                timestamp=timestamp(sub_elem.find('TIMESTAMP').text),
                score=float(sub_elem.find('SCORE').text)
            ) for sub_elem in elem]

    def __repr__(self):
        return f'<CensusScaleHistory #{self.info.id} {self.info.title}>'



class Dispatch:
    """A dispatch.

    Attributes:
        id: The dispatch id.  Use with the World dispatch shard until I
            manage to think of a better interface.
        title: The dispatch title.
        author: Nation that posted the dispatch.
        category: The dispatch category.
        subcategory: The dispatch subcategory.
        views: Number of times the dispatch got viewed.
        score: Votes te dispatch received.
        created: When the dispatch was created.
        edited: When the dispatch last got edited.  Equal to
            ``created`` for dispatches that were never edited.
        text: The dispatch text.  ``None`` if the dispatch came from
            anywhere other than the World dispatch shard.
    """
    id: int
    title: str
    author: str
    category: str
    subcategory: str
    views: int
    score: int
    created: datetime.datetime
    edited: datetime.datetime
    text: Optional[str]

    def __init__(self, elem):
        self.id = int(elem.get('id'))
        self.title = unscramble_encoding(
            html.unescape(elem.find('TITLE').text))
        self.author = elem.find('AUTHOR').text
        self.category = elem.find('CATEGORY').text
        self.subcategory = elem.find('SUBCATEGORY').text
        self.views = int(elem.find('VIEWS').text)
        self.score = int(elem.find('SCORE').text)

        created = int(elem.find('CREATED').text)
        # Otherwise it's 0 for dispatches that were never edited
        edited = int(elem.find('EDITED').text) or created
        self.created = timestamp(created)
        self.edited = timestamp(edited)

        self.text = None
        with suppress(AttributeError):
            self.text = unscramble_encoding(
                html.unescape(elem.find('TEXT').text))

    def __repr__(self):
        return f'<Dispatch id={self.id}>'


class PollOption:
    """An option in a poll.

    Attributes:
        text: Text of the option.
        voters: Nations that picked this option.
    """
    text: str
    voters: List[str]

    def __init__(self, elem):
        self.text = html.unescape(elem.findtext('OPTIONTEXT'))
        voters = elem.find('VOTERS').text
        self.voters = voters.split(':') if voters else []


class Poll:
    """A regional poll.

    Attributes:
        id: The poll id.
        title: The poll title.
        text: The poll text.
        region: Region the poll was posted in.
        author: Nation that posted the poll.
        options: The poll options.
    """
    id: int
    title: str
    text: Optional[str]
    region: str
    author: str
    start: datetime.datetime
    stop: datetime.datetime
    options: List[PollOption]

    def __init__(self, elem):
        self.id = int(elem.get('id'))
        self.title = html.unescape(elem.findtext('TITLE'))
        try:
            self.text = html.unescape(elem.findtext('TEXT'))
        except AttributeError:
            self.text = None
        self.region = elem.find('REGION').text
        self.author = elem.find('AUTHOR').text
        self.start = timestamp(elem.find('START').text)
        self.stop = timestamp(elem.find('STOP').text)
        self.options = [PollOption(option_elem)
                        for option_elem in elem.find('OPTIONS')]

    def __repr__(self):
        return f'<Poll id={self.id}>'



class Freedom:
    """Nation's `Freedoms`: three basic indicators of the nation's
    Civil Rights, Economy, and Political Freedom, as expressive
    adjectives.

    Attributes:
        civilrights: Nation's Civil Rights.
        economy: Nation's Economy.
        politicalfreedom: Nation's Political Freedom.
    """
    civilrights: str
    economy: str
    politicalfreedom: str

    def __init__(self, elem):
        self.civilrights = elem.find('CIVILRIGHTS').text
        self.economy = elem.find('ECONOMY').text
        self.politicalfreedom = elem.find('POLITICALFREEDOM').text


class FreedomScores:
    """Nation's `Freedoms`: three basic indicators of the nation's
    Civil Rights, Economy, and Political Freedom, as percentages.

    Attributes:
        civilrights: Nation's Civil Rights.
        economy: Nation's Economic Prosperity.
        politicalfreedom: Nation's Political Freedom.
    """
    civilrights: int
    economy: int
    politicalfreedom: int

    def __init__(self, elem):
        self.civilrights = int(elem.find('CIVILRIGHTS').text)
        self.economy = int(elem.find('ECONOMY').text)
        self.politicalfreedom = int(elem.find('POLITICALFREEDOM').text)


class Govt:
    """Nation's government expenditure, as percentages.

    Attributes:
        administration: The percentage of nation's budget spent on
            Administration.
        defence: The percentage of nation's budget spent on
            Defence.
        education: The percentage of nation's budget spent on
            Public Education.
        environment: The percentage of nation's budget spent on
            Enviromental Protection.
        healthcare: The percentage of nation's budget spent on
            Public Healthcare.
        commerce: The percentage of nation's budget spent on
            Industry.
        internationalaid: The percentage of nation's budget spent on
            International Aid.
        lawandorder: The percentage of nation's budget spent on
            Law & Order.
        publictransport: The percentage of nation's budget spent on
            Public Transportation.
        socialequality: The percentage of nation's budget spent on
            Social Policy.
        spirituality: The percentage of nation's budget spent on
            Spirituality.
        welfare: The percentage of nation's budget spent on
            Welfare.
    """
    administration: float
    defence: float
    education: float
    environment: float
    healthcare: float
    commerce: float
    internationalaid: float
    lawandorder: float
    publictransport: float
    socialequality: float
    spirituality: float
    welfare: float

    def __init__(self, elem):
        self.administration = float(elem.find('ADMINISTRATION').text)
        self.defence = float(elem.find('DEFENCE').text)
        self.education = float(elem.find('EDUCATION').text)
        self.environment = float(elem.find('ENVIRONMENT').text)
        self.healthcare = float(elem.find('HEALTHCARE').text)
        self.commerce = float(elem.find('COMMERCE').text)
        self.internationalaid = float(elem.find('INTERNATIONALAID').text)
        self.lawandorder = float(elem.find('LAWANDORDER').text)
        self.publictransport = float(elem.find('PUBLICTRANSPORT').text)
        self.socialequality = float(elem.find('SOCIALEQUALITY').text)
        self.spirituality = float(elem.find('SPIRITUALITY').text)
        self.welfare = float(elem.find('WELFARE').text)


class Sectors:
    """Components of a nation's economy.

    Attributes:
        blackmarket: Part of the economy taken up by Black Market.
        government: Part of the economy taken up by Government.
        industry: Part of the economy taken up by Private Industry.
        public: Part of the economy taken up by State-Owned Industry.
    """
    blackmarket: float
    government: float
    industry: float
    public: float

    def __init__(self, elem):
        self.blackmarket = float(elem.find('BLACKMARKET').text)
        self.government = float(elem.find('GOVERNMENT').text)
        self.industry = float(elem.find('INDUSTRY').text)
        self.public = float(elem.find('PUBLIC').text)



class Reclassification(NamedTuple):
    """Change in a `Freedom` classification or the WA Category.

    Attributes:
        before: The old category or `Freedom` adjective.
        after: The new category or `Freedom` adjective.
    """
    before: str
    after: str


class Reclassifications:
    """Reclassifications of the nation's `Freedoms` and WA Category.
    For convenience, this is falsey when no reclassifications occured.

    Attributes:
        civilrights: Reclassification of nation's Civil Rights.
        economy: Reclassification of nation's Economy.
        politicalfreedom: Reclassification of nation's Political Freedom.
        govt: Change of nation's World Assembly Category.
    """
    civilrights: Optional[Reclassification]
    economy: Optional[Reclassification]
    politicalfreedom: Optional[Reclassification]
    govt: Optional[Reclassification]

    def __init__(self, elem):
        self.civilrights = self.economy = \
            self.politicalfreedom = self.govt = None
        if elem is None:
            return
        attr_names = {
            '0': 'civilrights',
            '1': 'economy',
            '2': 'politicalfreedom',
            'govt': 'govt'
        }
        for sub_elem in elem:
            setattr(
                self, attr_names[sub_elem.get('type')],
                Reclassification(
                    before=sub_elem.find('FROM').text,
                    after=sub_elem.find('TO').text
                )
            )

    def __bool__(self):
        return (self.civilrights or self.economy
                or self.politicalfreedom or self.govt)


class CensusScaleChange:
    """Change in one of the World Census scales of a nation

    Attributes:
        info: Static information about the scale.
        score: The scale score, after the change.
        change: Change of the score.
        pchange: The semi-user-friendly percentage change NationStates
            shows by default.
    """
    info: ScaleInfo
    score: float
    change: float
    pchange: float

    def __init__(self, elem):
        self.info = census_info[int(elem.get('id'))]
        self.score = float(elem.find('SCORE').text)
        self.change = float(elem.find('CHANGE').text)
        self.pchange = float(elem.find('PCHANGE').text)


class IssueResult:
    """Result of an issue.

    Attributes:
        happening: The issue effect line.  Not a sentence, mind you --
            it's uncapitalized and does not end with a period.
            ``None`` if the issue was dismissed.
        census: Changes in census scores of the nation.
        banners: The banners unlocked by answering the issue.
        reclassifications: WA Category and Freedoms reclassifications.
        headlines: Newspaper headlines.  NationStates returns this
            field with unexpanded macros.  I did my best to try and
            expand them all client-side, however there does not exist
            a document in which they are formally defined (that is
            sort of a pattern throughout NationStates, maybe you've
            noticed), so I can only do so much.  Please report any
            unexpanded macros you encounter as bugs.
    """
    happening: Optional[str]
    census: List[CensusScaleChange]
    banners: List[Banner]
    reclassifications: Reclassifications
    headlines: List[str]

    def __init__(self, elem):
        with suppress(AttributeError):
            error = elem.find('ERROR').text
            if error == 'Invalid choice.':
                raise ValueError('invalid option')
            elif error == 'Issue already processed!':
                # I know it may not be obvious, but that's exactly
                # what NS is trying to say here.
                raise ValueError('invalid issue')
        assert elem.find('OK').text == '1'  # honestly no idea

        self.happening = elem.findtext('DESC')
        self.census = [
            CensusScaleChange(sub_elem) for sub_elem
            in elem.find('RANKINGS') or ()
        ]
        self.banners = [
            banner(sub_elem.text) for sub_elem
            in elem.find('UNLOCKS') or ()
        ]
        self.reclassifications = Reclassifications(
            elem.find('RECLASSIFICATIONS'))
        self.headlines = [
            sub_elem.text for sub_elem
            in elem.find('HEADLINES') or ()
        ]



class IssueOption:
    """An option of an issue.

    Attributes:
        text: The option text. May contain HTML elements and character
            references.
    """
    text: str

    def __init__(self, elem, issue):
        self._issue = issue
        self._id = int(elem.get('id'))
        self.text = elem.text

    def accept(self) -> Awaitable[IssueResult]:
        """Accept the option."""
        return self._issue._nation._accept_issue(self._issue.id, self._id)

    # TODO repr


class Issue:
    """An issue.

    Attributes:
        id: The issue id.
        title: The issue title.  May contain HTML elements and
            character references.
        text: The issue text.  May contain HTML elements and character
            references.
        author: Author of the issue, usually a nation.
        editor: Editor of the issue, usually a nation.
        options: Issue options.
        banners: URLs of issue banners.
    """
    id: int
    title: str
    text: str
    author: Optional[str]
    editor: Optional[str]
    options: List[IssueOption]
    banners: List[str]

    def __init__(self, elem, nation):
        self._nation = nation
        self.id = int(elem.get('id'))
        self.title = elem.find('TITLE').text
        self.text = elem.find('TEXT').text
        self.author = elem.findtext('AUTHOR')
        self.editor = elem.findtext('EDITOR')
        self.options = [
            IssueOption(sub_elem, self)
            for sub_elem in elem.findall('OPTION')
        ]
        def issue_banners(elem):
            for x in range(1, 10):  # Should be more than enough.
                try:
                    yield banner_url(elem.find(f'PIC{x}').text)
                except AttributeError:
                    break
        self.banners = list(issue_banners(elem))

    def dismiss(self) -> Awaitable[IssueResult]:
        """Dismiss the issue."""
        return self._nation._accept_issue(self.id, -1)

    # TODO repr



class Embassies:
    """Embassies of a region.

    Attributes:
        active: Normal, alive embassies.
        closing: Embassies the demolition of which has been initiated,
            but did not yet finish.
        pending: Embassies the creation of which has been initiated,
            but did not yet finish.
        invited: Embassy invitations that have not yet been processed.
        rejected: Embassy invitations that have been denied.
    """
    active: List[str]
    closing: List[str]
    pending: List[str]
    invited: List[str]
    rejected: List[str]

    def __init__(self, elem):
        # I know I'm iterating through them five times; I don't care.
        self.active = [sub_elem.text for sub_elem in elem
                       if sub_elem.get('type') is None]
        self.closing = [sub_elem.text for sub_elem in elem
                        if sub_elem.get('type') == 'closing']
        self.pending = [sub_elem.text for sub_elem in elem
                        if sub_elem.get('type') == 'pending']
        self.invited = [sub_elem.text for sub_elem in elem
                        if sub_elem.get('type') == 'invited']
        self.rejected = [sub_elem.text for sub_elem in elem
                         if sub_elem.get('type') == 'rejected']



class Authority(Flag):
    """Authority of a Regional Officer, Delegate, or Founder."""
    EXECUTIVE      = X = auto()
    WORLD_ASSEMBLY = W = auto()
    APPEARANCE     = A = auto()
    BORDER_CONTROL = B = auto()
    COMMUNICATIONS = C = auto()
    EMBASSIES      = E = auto()
    POLLS          = P = auto()

    @classmethod
    def _from_ns(cls, string):
        """This is the only sane way I could find to make Flag enums
        work with individual characters as flags.
        """
        return reduce(or_, (cls[char] for char in string))

    def __repr__(self):
        return f'<OfficerAuthority.{self.name}>'


class Officer:
    """A Regional Officer.

    Attributes:
        nation: Officer's nation.
        office: The (user-specified) office held by the officer.
        authority: Officer's authority.
        appointed_at: When the officer got appointed.
        appointed_by: The nation that appointed the officer.
    """
    nation: str
    office: str
    authority: Authority
    appointed_at: datetime.datetime
    appointed_by: str

    def __init__(self, elem):
        self.nation = elem.find('NATION').text
        self.office = elem.findtext('OFFICE')
        self.authority = Authority._from_ns(elem.find('AUTHORITY').text)
        self.appointed_at = timestamp(elem.find('TIME').text)
        self.appointed_by = elem.find('BY').text



@total_ordering
class EmbassyPostingRights(Enum):
    """Who out of embassy regions' residents can post on the Regional
    Message Board.
    """
    NOBODY = 1
    DELEGATES_AND_FOUNDERS = 2
    COMMUNICATIONS_OFFICERS = 3
    OFFICERS = 4
    EVERYBODY = 5

    @classmethod
    def _from_ns(cls, string):
        values = {
            '0': 1,  # The reason I have to do all this nonsense.
            'con': 2,
            'com': 3,
            'off': 4,
            'all': 5,
        }
        return cls(values[string])

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented


class PostStatus(Enum):
    """Status of a post on a Regional Message Board.

    Attributes:
        NORMAL: A regular post.
        SUPPRESSED: The post got suppressed by a regional official.
        DELETED: The post got deleted by its author.
        MODERATED: The post got suppressed by a game moderator.
    """
    NORMAL = 0
    SUPPRESSED = 1
    DELETED = 2
    MODERATED = 9

    @property
    def viewable(self) -> bool:
        """Whether the post content can still be accessed.  Shortcut
        for ``PostStatus.NORMAL or PostStatus.SUPPRESSED``.
        """
        return self.value in (0, 1)


class Post:
    """A post on a Regional Message Board.

    Attributes:
        id: The unique (or so it would seem) id of the post.
        timestamp: When the post was, well, posted.
        author: The author nation.
        status: Status of the post.
        text: The post text.
        likers: Nations that liked the post.
        suppressor: Nation that suppressed the post.  ``None`` if the
            post has not been suppressed.
    """
    id: int
    timestamp: datetime.datetime
    author: str
    status: PostStatus
    text: str
    likers: List[str]
    suppressor: Optional[str]

    def __init__(self, elem):
        self.id = int(elem.get('id'))
        self.timestamp = timestamp(elem.find('TIMESTAMP').text)
        self.author = elem.find('NATION').text
        self.status = PostStatus(int(elem.find('STATUS').text))
        self.text = elem.find('MESSAGE').text  # TODO unescape?

        likers_elem = elem.find('LIKERS')
        self.likers = likers_elem.text.split(':') if likers_elem else []
        self.suppressor = elem.findtext('SUPPRESSOR')

    # TODO repr



class Zombie:
    """The situation in a nation/region during the annual Z-Day event.

    Attributes:
        survivors: The number of citizens surviving, in millions.
        zombies: The number of undead citizens, in millions.
        dead: The number of dead citizens, in millions.
        action: The nation's strategy for dealing with the disaster.
            Either "research", "exterminate", or "export".  ``None``
            if the instance represents regional situation.
    """
    survivors: int
    zombies: int
    dead: int
    action: Optional[str]

    def __init__(self, elem):
        self.survivors = int(elem.find('SURVIVORS').text)
        self.zombies = int(elem.find('ZOMBIES').text)
        self.dead = int(elem.find('DEAD').text)
        self.action = elem.findtext('ZACTION')



class ArchivedHappening:
    """An archived happening.  NationStates doesn't store ids of those,
    for whatever reason.

    Attributes:
        timestamp: Time of the happening.
        text: The happening text.
    """
    timestamp: datetime.datetime
    text: str

    def __init__(self, elem):
        self.timestamp = timestamp(elem.find('TIMESTAMP').text)
        self.text = elem.findtext('TEXT')


class Happening(ArchivedHappening):
    """A happening.

    Attributes:
        id: The happening id.
        timestamp: Time of the happening.
        text: The happening text.
    """
    id: int

    def __init__(self, elem):
        self.id = int(elem.get('id'))
        super().__init__(elem)

    def __repr__(self):
        return f'<Happening #{self.id}>'


# TODO gavote, scvote



