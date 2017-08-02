"""datareader.news.py: tools for fetching stock news"""
from datetime import datetime
import itertools
from os import path
import warnings

import demjson
import requests
from six.moves.html_parser import HTMLParser

from prosper.datareader.config import LOGGER as G_LOGGER
import prosper.datareader.exceptions as exceptions

LOGGER = G_LOGGER
HERE = path.abspath(path.dirname(__file__))
#PARSER = HTMLParser()

def validate_google_response(response, tag_primary=True):
    """crunches down google response for return

    Args:
        response (:obj:`dict`): data from google response
        tag_primary (bool, optional): certain articles exist at front of lists, mark them

    Returns:
        (:obj:`list`): list of parsed news articles

    """
    article_list = []
    for block in response['clusters']:
        if int(block['id']) == -1:
            continue # final entry is weird

        for index, story in enumerate(block['a']):
            ## Tag primary sources ##
            if index == 0 and tag_primary:
                story['primary'] = True
            elif tag_primary:
                story['primary'] = False

            ## Clean up HTML ##
            story['t'] = HTMLParser().unescape(story['t'])
            story['sp'] = HTMLParser().unescape(story['sp'])

            ## ISO datetime ##
            story['tt'] = datetime.fromtimestamp(int(story['tt'])).isoformat()

            article_list.append(story)

    return article_list

def pretty_return_google_news(results, keep_google_links=False):
    """recast keys shorthand->human in google result

    Args:
        results (:obj:`list`): google news results
        keep_google_links (bool): save the google traceback information

    Returns:
        (:obj:`list`): human-friendly results, JSONable

    """
    pretty_results = []
    for article in results:
        pretty = {}
        pretty['source'] = article['s']
        pretty['url'] = article['u']
        pretty['title'] = article['t']
        pretty['blurb'] = article['sp']
        pretty['datetime'] = article['tt']
        pretty['age'] = article['d']
        if keep_google_links:
            pretty['usg'] = article['usg']
            pretty['sru'] = article['sru']
        if 'primary' in article:
            pretty['primary'] = article['primary']

        pretty_results.append(pretty)

    return pretty_results

GOOGLE_COMPANY_NEWS = 'https://www.google.com/finance/company_news'
def fetch_company_news_google(
        ticker,
        pretty=False,
        keep_google_links=False,
        uri=GOOGLE_COMPANY_NEWS,
        logger=LOGGER
):
    """fetch news for one company ticker

    Args:
        ticker (str): ticker for company
        pretty (bool, optional): recast short->pretty keys
        keep_google_links (bool, optional): save the google traceback information
        uri (str, optional): endpoint URI for `company_news`
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`list`): processed news results, JSONable

    """
    logger.info('fetching company_news for %s', ticker)

    params = {
        'q': ticker,
        'output': 'json'
    }
    logger.debug(uri)
    req = requests.get(uri, params=params)
    req.raise_for_status()

    articles_list = []
    try:
        raw_articles = demjson.decode(req.text)
    except Exception as err: #pragma: no cover
        #No coverage: blank news has no single ticker
        logger.debug(req.text)
        if str(err) == 'Can not decode value starting with character \'<\'': #pragma: no cover
            #demjson does not raise unique exceptions :<
            logger.warning('empty news endpoint for %s @ %s', ticker, uri)
            return articles_list
        else:
            logger.error('Unable to parse news items for %s @ %s', ticker, uri, exc_info=True)
            raise err

    logger.info('parsing news object for %s', ticker)
    articles_list = validate_google_response(raw_articles)

    if pretty:
        logger.info('pretty printing article keys')
        articles_list = pretty_return_google_news(articles_list, keep_google_links)

    return articles_list

GOOGLE_MARKET_NEWS = 'https://www.google.com/finance/market_news'
def fetch_market_news_google(
        pretty=False,
        keep_google_links=False,
        uri=GOOGLE_MARKET_NEWS,
        logger=LOGGER
):
    """Fetches generic market news for the day

    Note:
        Wrapped function for `fetch_company_news_google` on a different endpoint


    Args:
        pretty (bool, optional): recast short->pretty keys
        keep_google_links (bool, optional): save the google traceback information
        uri (str, optional): endpoint URI for `market_news`
        logger (:obj:`logging.logger`, optional): logging handle
    Returns:
        (:obj:`list`): processed news results, JSONable

    """
    logger.info('--wrapping `fetch_company_news_google() with uri=%s', uri)

    return fetch_company_news_google(
        '',
        pretty=pretty,
        keep_google_links=keep_google_links,
        uri=uri,
        logger=logger
    )

RH_NEWS = 'https://api.robinhood.com/midlands/news/'
PAGE_HARDBREAK = 50
def fetch_company_news_rh(
        ticker,
        page_limit=None,
        uri=RH_NEWS,
        logger=LOGGER
):
    """parse news feed from robhinhood

    Args:
        ticker (str): ticker for desired stock
        page_limit (int, optional): number of pages to fetch to cap results

        uri (str, optional): endpoint address
        logger (:obj:`logging.logger`, optional): logging handle

    Returns:
        (:obj:`list`): collection of news articles from robinhood

    """
    logger.info('fetching company_news for %s', ticker)
    page = itertools.count(start=1, step=1)

    articles_list = []
    while True:
        ## Generate request ##
        page_num = next(page)

        params = {
            'page': page_num,
            'symbol': ticker.upper()    #caps required
        }
        logger.info('--fetching page %s for %s from %s', page_num, ticker, uri)

        ## GET data ##
        req = requests.get(uri, params=params)
        req.raise_for_status()
        page_data = req.json()

        articles_list.extend(page_data['results'])

        ## Loop or quit ##
        if page_limit and page_num >= page_limit:
            logger.info('--reached page limit: %s:%s', page_num, page_limit)
            break

        if not page_data['next']:
            #NOTE: page_data['next'] does not yield a valid address.  Manually step
            logger.info('--no more pages on endpoint %s', page_num)
            break

        if page_num > PAGE_HARDBREAK:
            warnings.warn(
                'pagination limit {} reached'.format(PAGE_HARDBREAK),
                exceptions.PaginationWarning
            )
            break

    return articles_list
