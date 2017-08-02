#!/usr/bin/env python3
import sys
import getopt
import logging
from importlib import import_module
from known_sites import SITES
from utils import r_get, multithre_downloader

def main(url):
    global proxy
    global module
    lib_path = None
    if not url.startswith('http://') and not url.startswith('https://'):
        url = 'http://' + url
    if not module:
        for k in SITES.keys():
            if k in url:
                lib_path = 'dl-lib.' + SITES[k]
                break
        if not lib_path:
            logger.warning(help_message)
            logger.warning('{} not supported'.format(url))
            return -1
    elif module: 
        if module in SITES.keys():
            lib_path = 'dl-lib.' + module
        else:
            logger.warning(help_message)
            logger.warning('{} not supported'.format(module))
            return -1

    m = import_module(lib_path)
    logger.info("processing %s", url)
    web_page = r_get(url, proxy=proxy).text
    ret = m.return_dic(web_page)
    logger.info("processing %s - %s", ret.get('author', 'No author found'), ret.get('title', 'No title found'))
    try:
        assert ret['pics'] != []
        multithre_downloader(dic=ret, proxy=proxy)
    except AssertionError:
        logger.error('No Link Found, {}'.format(url))
    finally:
        return 0
    return 0

help_message = '''Supported sites: {}
Usage: pic-dl [OPTION] [URL]
\t-x|--proxy scheme://host:port
\t-m|--module specify module
\t-h|--help
'''.format('\n\t' + '\n\t'.join(list(SITES.keys())))

if __name__ == '__main__':
    proxy = None
    module = None

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger()
    logger.setLevel('INFO')

    short_opts = "Vvhx:m:"
    opts = ['version', 'proxy=', 'module=','help', 'verbose']

    try:
        opts, args = getopt.getopt(sys.argv[1:], short_opts, opts)
    except getopt.GetoptError as err:
        logger.error(err)
        print(help_message)
        sys.exit(2)

    for k, v in opts:
        if k == '-x' or k == '--proxy':
            proxy = v
        elif k == '-m' or k == '--module':
            module = v
        elif k == '-h' or k == '--help':
            print(help_message)
            sys.exit(0)
        elif k == '-v' or k == '--verbose':
            logger.setLevel('DEBUG')

    for i in args:
        main(i)
