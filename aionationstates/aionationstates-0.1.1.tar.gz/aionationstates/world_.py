from contextlib import suppress
from asyncio import get_event_loop, sleep, CancelledError

from aionationstates.session import Session, api_query
from aionationstates.types import Dispatch, Poll, Happening
from aionationstates.shards import Census
from aionationstates.ns_to_human import dispatch_categories, happening_filters
from aionationstates.utils import utc_seconds, normalize

# Needed for type annotations
import datetime
from typing import List, AsyncIterator, Iterable, Union
from asyncio import Task
from aionationstates.session import ApiQuery


class World(Census, Session):
    """Interface to the NationStates World API."""

    @api_query('featuredregion')
    async def featuredregion(self, root) -> str:
        """Today's featured region."""
        return root.find('FEATUREDREGION').text

    @api_query('newnations')
    async def newnations(self, root) -> List[str]:
        """Most recently founded nations, from newest."""
        return root.find('NEWNATIONS').text.split(',')

    @api_query('nations')
    async def nations(self, root) -> List[str]:
        """List of all the nations, seemingly in order of creation."""
        return root.find('NATIONS').text.split(',')

    @api_query('numnations')
    async def numnations(self, root) -> int:
        """Total number of nations."""
        return int(root.find('NUMNATIONS').text)

    @api_query('regions')
    async def regions(self, root) -> List[str]:
        """List of all the regions, seemingly in order of creation.
        Not normalized.
        """
        return root.find('REGIONS').text.split(',')  # TODO normalize?

    @api_query('numregions')
    async def numregions(self, root) -> int:
        """Total number of regions."""
        return int(root.find('NUMREGIONS').text)

    def regionsbytag(self, *tags: str) -> ApiQuery[List[str]]:
        """All regions belonging to any of the named tags.  Tags can be
        preceded by a ``-`` to select regions without that tag.
        """
        if len(tags) > 10:
            raise ValueError('You can specify up to 10 tags')
        if not tags:
            raise ValueError('No tags specified')
        # We don't check for invalid tags here because the behaviour is
        # fairly intuitive - quering for a non-existent tag returns no
        # regions, excluding it returns all of them.
        @api_query('regionsbytag', tags=','.join(tags))
        async def result(_, root):
            text = root.find('REGIONS').text  # TODO normalize?
            return text.split(',') if text else []
        return result(self)

    def dispatch(self, id: int) -> ApiQuery[Dispatch]:
        """Dispatch by id.  Primarily useful for getting dispatch
        texts, as this is the only way to do so.
        """
        @api_query('dispatch', dispatchid=str(id))
        async def result(_, root):
            elem = root.find('DISPATCH')
            if not elem:
                raise ValueError(f'No dispatch found with id {id}')
            return Dispatch(elem)
        return result(self)

    def dispatchlist(self, *, author: str = None, category: str = None,
                     subcategory: str = None, sort: str = 'new'
                     ) -> ApiQuery[List[Dispatch]]:
        """Find dispatches by certain criteria.

        Parameters:
            author: Nation authoring the dispatch.
            category: Dispatch's primary category.
            subcategory: Dispatch's secondary category.
            sort: Sort order, 'new' or 'best'.
        """
        params = {'sort': sort}
        if author:
            params['dispatchauthor'] = author
        # Here we do need to ensure that our categories are valid, cause
        # NS just ignores the categories it doesn't recognise and returns
        # whatever it feels like.
        if category and subcategory:
            if (category not in dispatch_categories or
                    subcategory not in dispatch_categories[category]):
                raise ValueError('Invalid category/subcategory')
            params['dispatchcategory'] = f'{category}:{subcategory}'
        elif category:
            if category not in dispatch_categories:
                raise ValueError('Invalid category')
            params['dispatchcategory'] = category

        @api_query('dispatchlist', **params)
        async def result(_, root):
            return [
                Dispatch(elem)
                for elem in root.find('DISPATCHLIST')
            ]
        return result(self)

    def poll(self, id: int) -> ApiQuery[Poll]:
        """Poll with a given id."""
        @api_query('poll', pollid=str(id))
        async def result(_, root):
            elem = root.find('POLL')
            if not elem:
                raise ValueError(f'No poll found with id {id}')
            return Poll(elem)
        return result(self)

    # Happenings interface:

    def _get_happenings(self, *, nation, region, filter, limit=100,
                        beforeid=None, beforetime=None):
        params = {'limit': str(limit)}
        if filter:
            filter = (filter,) if type(filter) is str else filter
            for filter_item in filter:
                if filter_item not in happening_filters:
                    raise ValueError(f'No such filter "{filter_item}"')
            params['filter'] = '+'.join(filter)

        if nation and region:
            raise ValueError('You cannot specify both nation and region views')
        if nation:
            nation = (nation,) if type(nation) is str else nation
            nation = '+'.join(map(normalize, nation))
            params['view'] = f'nation.{nation}'
        elif region:
            region = (region,) if type(region) is str else region
            region = '+'.join(map(normalize, region))
            params['view'] = f'region.{region}'

        if beforetime:
            params['beforetime'] = str(utc_seconds(beforetime))
        elif beforeid:
            params['beforeid'] = str(beforeid)

        @api_query('happenings', **params)
        async def result(_, root):
            return [Happening(elem) for elem in root.find('HAPPENINGS')]
        return result(self)

    async def happenings(
            self, *,
            nation: Union[str, Iterable[str]] = None,
            region: Union[str, Iterable[str]] = None,
            filter: Union[str, Iterable[str]] = None,
            beforeid: int = None,
            beforetime: datetime.datetime = None
            ) -> AsyncIterator[Happening]:
        """Iterate through happenings from newest to oldest.

        Parameters:
            nation: Nation(s) happenings of which will be requested.
                Cannot be specified at the same time with region.
            region: Region(s) happenings of which will be requested.
                Cannot be specified at the same time with nation.
            filter: Category(s) to request happenings by.  Available
                filters are: 'law', 'change', 'dispatch', 'rmb',
                'embassy', 'eject', 'admin', 'move', 'founding', 'cte',
                'vote', 'resolution', 'member', and 'endo'.
            beforeid: Only request happenings before this id.
            beforetime: Only request happenings before this moment.
        """
        while True:
            happening_bunch = await self._get_happenings(
                nation=nation, region=region, filter=filter,
                beforeid=beforeid, beforetime=beforetime
            )
            for happening in happening_bunch:
                yield happening
            if len(happening_bunch) < 100:
                break
            beforeid = happening_bunch[-1].id

    async def new_happenings(
            self, poll_period: int = 30, *,
            nation: Union[str, Iterable[str]] = None,
            region: Union[str, Iterable[str]] = None,
            filter: Union[str, Iterable[str]] = None
            ) -> AsyncIterator[Happening]:
        """An asynchronous generator that yields new happenings as they
        arrive::

            async for happening in \
                    world.new_happenings(region='the north pacific'):
                # Your processing code here
                print(happening.text)  # As an example

        Guarantees that:

        * Every happening is generated from the moment the generator
          is started;
        * No happening is generated more than once;
        * Happenings are denerated in order from oldest to newest.

        Parameters:
            poll_period: How long to wait between requesting the next
                bunch of happenings.  Note that this should only be
                tweaked for latency reasons, as the function gives a
                guarantee that all happenings will be generated.
                Also note that, regardless of the ``poll_period`` you
                set, all of the code in your loop body still has to
                execute (possibly several times) before a new bunch of
                happenings can be requested.  Consider wrapping your
                happening-processing code in a coroutine and launching
                it as a task from the loop body if you suspect this
                might be an issue.
            nation: Nation(s) happenings of which will be requested.
                Cannot be specified at the same time with region.
            region: Region(s) happenings of which will be requested.
                Cannot be specified at the same time with nation.
            filter: Category(s) to request happenings by.  Available
                filters are: 'law', 'change', 'dispatch', 'rmb',
                'embassy', 'eject', 'admin', 'move', 'founding', 'cte',
                'vote', 'resolution', 'member', and 'endo'.
        """
        try:
            # We only need the happenings from this point forwards
            last_id = (await self._get_happenings(
                nation=nation, region=region, filter=filter, limit=1))[0].id
        except IndexError:
            # Happenings before this point have all been deleted
            last_id = 0

        while True:
            # Sleep before the loop body to avoid wasting the first request
            await sleep(poll_period)

            # I don't think there's a cleaner solution, sadly.
            happenings = []
            async for happening in self.happenings(
                    nation=nation, region=region, filter=filter):
                if happening.id <= last_id:
                    break
                happenings.append(happening)

            with suppress(IndexError):
                last_id = happenings[0].id

            for happening in reversed(happenings):
                yield happening


