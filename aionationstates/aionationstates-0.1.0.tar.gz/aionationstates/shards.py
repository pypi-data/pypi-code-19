"""Interfaces to shards shared between APIs. Designed to be mixed in
with Session, otherwise useless."""

# TODO: happenings (region history as well?), censusranks, wabadges

from aionationstates.types import CensusScaleCurrent, CensusScaleHistory
from aionationstates.session import api_query

# Needed for type annotations
from typing import List
from aionationstates.session import ApiQuery


class Census:
    def census(self, *scales: int) -> ApiQuery[List[CensusScaleCurrent]]:
        """Current World Census data.

        By default returns data on today's featured World Census
        scale, use arguments to get results on specific scales.  In
        order to request data on all scales at once you can do
        ``x.census(*range(81))``.

        Parameters:
            scales: World Census scales, integers between 0 and 80.
        """
        params = {'mode': 'score+rank+rrank+prank+prrank'}
        if scales:
            params['scale'] = '+'.join(str(x) for x in scales)
        @api_query('census', **params)
        async def result(_, root):
            return [
                CensusScaleCurrent(scale_elem)
                for scale_elem in root.find('CENSUS')
            ]
        return result(self)


    def censushistory(self, *scales: int
                      ) -> ApiQuery[List[CensusScaleHistory]]:
        """Historical World Census data.

        Was split into its own method for the sake of simplicity and
        intuitiveness when combinind shards.

        By default returns data on today's featured World Census
        scale, use arguments to get results on specific scales.  In
        order to request data on all scales at once you can do
        ``x.censushistory(*range(81))``.

        Returns data for the entire length of history NationStates
        stores.  There is no way to override that.

        Parameters:
            scales: World Census scales, integers between 0 and 80.
        """
        params = {'mode': 'history'}
        if scales:
            params['scale'] = '+'.join(str(x) for x in scales)
        @api_query('census', **params)
        async def result(_, root):
            return [
                CensusScaleHistory(scale_elem)
                for scale_elem in root.find('CENSUS')
            ]



