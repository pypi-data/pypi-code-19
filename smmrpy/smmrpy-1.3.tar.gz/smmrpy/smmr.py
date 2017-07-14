import aiohttp

from .smmry import SMMRY

class SMMRPY:

    def __init__(self, api_key):
        self.api_key = api_key

        self.url = r'http://api.smmry.com/'

    async def get_smmry(self, url : str, **kwargs):

        length = kwargs.get('length', 7)
        keywords = kwargs.get('keyword_count', 5)
        quotes = kwargs.get('quotes', True)
        breaks = kwargs.get('breaks', False)

        params = {
            'SM_API_KEY' : self.api_key,
            'SM_LENGTH' : length,
            'SM_KEYWORD_COUNT' : keywords,
            'SM_QUOTE_AVOID' : str(not quotes).lower(),
            'SM_WITH_BREAK' : str(breaks).lower(),
            'SM_URL' : url
        }

        async with aiohttp.ClientSession().get(self.url, params=params) as rawdata:
            data = await rawdata.json()

        error_code = data.get('sm_api_error')
        message = data.get('sm_api_message')

        if error_code:
            if error_code == 0:
                raise InternalServerError(message)
            elif error_code == 1:
                raise IncorrectSubmissionVariables(message)
            elif error_code == 2:
                raise IntentialRestriction(message)
            elif error_code == 3:
                raise SummarizationError(message)
            else:
                raise GenericError('We failed and don\'t know why :(')

        return(SMMRY(data))

class InternalServerError(Exception):
    pass

class IncorrectSubmissionVariables(Exception):
    pass

class IntentialRestriction(Exception):
    pass

class SummarizationError(Exception):
    pass
