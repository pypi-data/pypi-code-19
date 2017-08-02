#!/usr/bin/env python3
import sys
import logging
import argparse
from importlib import import_module
from .known_sites import *
from .utils import r_get, multithre_downloader, r0

logging.basicConfig(
    level=logging.INFO,
    format="%(message)s")
logger = logging.getLogger()
logger.setLevel("INFO")


def _main(url, proxy, module):
    lib_path = None
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url.rstrip("/")
    domain = r0(r'^https?:\/\/([^\/]+)\/', url)
    domain = ''.join(domain)
    if "weibo.com" in domain:
        url = "http://m.weibo.cn/status/" + url.split("?")[0].rstrip("/").split("/")[-1]
    mod = url.rstrip("/").split("/")[-1]
    if not module:
        for k in SITES.keys():
            if k in domain:
                mod = "[{}] [{}]".format(k, mod)
                lib_path = "pic_dl.extractor." + SITES[k]
                break
        if not lib_path:
            logger.warning(description)
            logger.warning("{} not supported".format(url))
            return -1
    elif module:
        if module in SITES.keys():
            mod = "[{}] [{}]".format(module, mod)
            lib_path = "pic_dl.extractor." + module
        else:
            logger.warning(description)
            logger.warning("{} not supported".format(module))
            return -1

    m = import_module(lib_path)
    logger.info("{}: {}".format(mod, url))
    logger.info("{}: {}".format(mod, "Downloading webpage"))
    web_page = r_get(url, proxy=proxy).text
    logger.info("{}: {}".format(mod, "Extracting links"))
    ret = m.return_dic(web_page)
    logger.info("{}: {} - {}".format(mod, ret.get("author", "No author found"), ret.get("title", "No title found")))
    try:
        assert ret["pics"] != []
        logger.info("{}: Total pics: {}".format(mod, len(ret["pics"])))
        multithre_downloader(dic=ret, proxy=proxy, mod=mod)
    except AssertionError:
        logger.error("{}: No Link Found, {}".format(mod, url))
    finally:
        return 0
    return 0


def main():
    if "-V" in sys.argv or "--version" in sys.argv:
        print(version)
        return 0

    parser = argparse.ArgumentParser(description=description,
                                     formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument("-x", "--proxy",
                        help="set proxy",
                        required=False,
                        dest="proxy",
                        default=None)
    parser.add_argument("-m", "--module",
                        help="specify module",
                        dest="module",
                        default=None)
    parser.add_argument("-v", "--verbose",
                        help="set verbose",
                        action="store_true",
                        dest="verbose",
                        default=False)
    parser.add_argument("-V", "--version",
                        help="print version info",
                        action="store_true",
                        dest="version",
                        default=False)
    parser.add_argument("link",
                        type=str,
                        nargs="+",
                        help="one or more link")

    args = vars(parser.parse_args())
    if args["verbose"]:
        logger.setLevel("DEBUG")

    logger.debug(args)
    proxy = args["proxy"]
    module = args["module"]

    for i in args["link"]:
        _main(i, proxy, module)


if __name__ == "__main__":
    main()
