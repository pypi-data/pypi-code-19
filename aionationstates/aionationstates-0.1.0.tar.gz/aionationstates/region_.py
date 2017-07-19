import html

from aionationstates.utils import normalize, timestamp
from aionationstates.types import (
    EmbassyPostingRights, Officer, Authority, Embassies, Zombie, Poll,
    ArchivedHappening)
from aionationstates.session import Session, api_query
from aionationstates.shards import Census

# Needed for type annotations
import datetime
from typing import Optional, List


class Region(Census, Session):
    """A class to interact with the NationStates Region API.

    Attributes:
        id: The defining characteristic of a region, its normalized
            name.  No two regions share the same id, and no one id
            is shared by multiple regions.
    """
    id: str

    def __init__(self, name: str) -> None:
        self.id = normalize(name)

    def _call_api(self, params, *args, **kwargs):
        params['region'] = self.id
        return super()._call_api(*args, params=params, **kwargs)


    @api_query('name')
    async def name(self, root) -> str:
        """Name of the region."""
        return root.find('NAME').text

    @api_query('flag')
    async def flag(self, root) -> str:
        """URL of the region's flag."""
        return root.find('FLAG').text

    @api_query('factbook')
    async def factbook(self, root) -> str:
        """Region's World Factbook Entry."""
        # This lib might have been a mistake, but the line below
        # definitely isn't.
        return html.unescape(html.unescape(root.find('FACTBOOK').text))

    @api_query('power')
    async def power(self, root) -> str:
        """An adjective describing region's power on the interregional
        scene.
        """
        return root.find('POWER').text

    @api_query('delegatevotes')
    async def delegatevotes(self, root) -> int:
        """Number of the World Assembly votes the region's Delegate
        has.
        """
        return int(root.find('DELEGATEVOTES').text)

    @api_query('numnations')
    async def numnations(self, root) -> int:
        """The number of nations in the region."""
        return int(root.find('NUMNATIONS').text)

    @api_query('foundedtime')
    async def founded(self, root) -> datetime.datetime:
        """When the region was founded."""
        return timestamp(root.find('FOUNDEDTIME'))

    @api_query('nations')
    async def nations(self, root) -> List[str]:
        """All the nations in the region."""
        text = root.find('NATIONS').text
        return text.split(':') if text else []

    @api_query('embassies')
    async def embassies(self, root) -> Embassies:
        """Embassies the region has."""
        return Embassies(root.find('EMBASSIES'))

    @api_query('embassyrmb')
    async def embassyrmb(self, root) -> EmbassyPostingRights:
        """Posting rights for members the of embassy regions."""
        return EmbassyPostingRights._from_ns(root.find('EMBASSYRMB').text)

    @api_query('delegate')
    async def delegate(self, root) -> Optional[str]:
        """Regional World Assembly Delegate.  ``None`` if the region
        has no delegate.
        """
        nation = root.find('DELEGATE').text
        if nation == '0':
            return None
        return nation

    @api_query('delegateauth')
    async def delegateauth(self, root) -> Authority:
        """Regional World Assembly Delegate's authority.  Always set,
        no matter if the region has a delegate or not.
        """
        return Authority._from_ns(root.find('DELEGATEAUTH').text)

    @api_query('founder')
    async def founder(self, root) -> Optional[str]:
        """Regional Founder.  Returned even if the nation has ceased to
        exist.  ``None`` if the region is Game-Created and doesn't have
        a founder.
        """
        nation = root.find('FOUNDER').text
        if nation == '0':
            return None
        return nation

    @api_query('founderauth')
    async def founderauth(self, root) -> Authority:
        """Regional Founder's authority.  Always set,
        no matter if the region has a founder or not.
        """
        return Authority._from_ns(root.find('FOUNDERAUTH').text)

    @api_query('officers')
    async def officers(self, root) -> List[Officer]:
        """Regional Officers.  Does not include the Founder or
        the Delegate, unless they have additional litles as Officers.
        In the correct order.
        """
        officers = sorted(
            root.find('OFFICERS'),
            # I struggle to say what else this tag would be useful for.
            key=lambda elem: int(elem.find('ORDER').text)
        )
        return [Officer(elem) for elem in officers]

    @api_query('tags')
    async def tags(self, root) -> List[str]:
        """Tags the region has."""
        return [elem.text for elem in root.find('TAGS')]

    @api_query('zombie')
    async def zombie(self, root) -> Zombie:
        """Region's state during the annual Z-Day event."""
        return Zombie(root.find('ZOMBIE'))

    @api_query('poll')
    async def poll(self, root) -> Optional[Poll]:
        """Current regional poll."""
        elem = root.find('POLL')
        return Poll(elem) if elem else None

    @api_query('happenings')
    async def happenings(self, root) -> List[ArchivedHappening]:
        """Get the happenings of the region, the ones archived on its
        in-game page.  Newest to oldest.
        """
        return [ArchivedHappening(elem) for elem in root.find('HAPPENINGS')]

    # TODO: history, messages


