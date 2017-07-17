#!python3

"""
Trawl web pages for files to download
"""

import urllib.request
import urllib.parse
import urllib.error
import html.parser
import contextlib
import collections
import argparse
import logging
import os.path
import multiprocessing
import multiprocessing.pool
import fnmatch
import sys


# This namedtuple has to be defined outside of functions to be picklable for multiprocessing
Link = collections.namedtuple("Link", "href mb type")


class MyHTMLParser(html.parser.HTMLParser):
    """ Parses HTML for hrefs in a tags
    """
    hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            for name, value in attrs:
                if name == "href":
                    self.hrefs.append(value)


def _parse_args():
    """ Parses command line arguments and returns named tuple with argument value.
    """
    parser = argparse.ArgumentParser(
        description=("Downloads all files linked to on a given web pages"),
        prog="web_trawler"
    )
    parser.add_argument("url")
    parser.add_argument("--target", "-t", default="download")
    parser.add_argument("--add_links_from_linked_pages", "-a", action="store_true")
    parser.add_argument("--quiet", "-q", action="store_true")
    parser.add_argument("--processes", "-p", type=int, default=None)
    parser.add_argument("--whitelist", "-w", type=str, default=None)
    parser.add_argument("--blacklist", "-b", type=str, default=None)
    parser.add_argument("--no_of_files_limit", "-n", type=int, default=None)
    parser.add_argument("--mb_per_file_limit", "-m", type=float, default=None)
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--interactive_download_prompt", "-I", action="store_true")
    args = parser.parse_args()
    return args


def _query_yes_no(question, default=None):
    """ Helper function to prompt user for input
    """
    valid = {
        "yes": True,
        "y": True,
        "no": False,
        "n": False
    }

    if default == None:
        prompt = " [y/n]"
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def _compose_link_info_tuple(href):
    """
    For parallel processing of http requests for headers.

    Parameters
    ----------
    href : str

    Returns
    -------
    namedtuple with
        href : string
        mb : string
            File size in MB calculated from content-length from http header
        type : string
            Unaltered from "content-type" field from http header
    """

    def get_from_header(href):
        """
        HTTP requests header, which is used to fill out the link information

        Parameters
        ----------
        href : str

        Returns
        -------
        mb : str
            File size in MB calculated from content-length from http header
        content_type : str
            Unaltered from "content-type" field from http header
        """

        mb = content_type = "?"
        try:
            with contextlib.closing(urllib.request.urlopen(href)) as response:
                header = response.info()
        except urllib.error.HTTPError as e:
            logging.warning("HTTPError requesting header for %s: %s" % (href, e))
            return False
        else:
            try:
                mb = "{0:.3f}".format(int(header["content-length"]) / 1000000)
            except TypeError as e:
                logging.debug("HTTP header did not contain content-length: %s" % e)
            content_type = header["content-type"]

        return (mb, content_type)

    returned = get_from_header(href)
    if returned:
        mb = returned[0]
        content_type = returned[1]
    else:
        return None

    logging.info("Adding link: %s MB: %s" % (mb, href))
    return Link(href=href, mb=mb, type=content_type)


def _get_max_no_of_processes(user_input):
    """ Get number of processes to delegate tasks to - default is the number of processors available minus one.
    """
    if user_input is None:
        all_but_one = multiprocessing.cpu_count() - 1
        no_of_processors = all_but_one if all_but_one > 0 else 1
    elif user_input >= 1:
        no_of_processors = user_input
    else:
        raise ValueError("There has to be at least one process")
    return no_of_processors


def _download_file(link_info_tuple):
    """ For parallel downloading of files.
    """
    logging.info("Downloading %s (%s MB)" % (link_info_tuple[0], link_info_tuple[2]))
    urllib.request.urlretrieve(link_info_tuple[0], link_info_tuple[1])


def _delegate_downloads_to_threads(link_info_tuples):
    """ Helper function to spawn up to 10 simultaneous threads for each process for downloads.
    """
    with multiprocessing.pool.ThreadPool(10) as thread_pool:
        thread_pool.map(_download_file, link_info_tuples)


def get_links(url):
    """
    Find everything linked to from a web page.

    Parameters
    ----------
    url : str
        To be interpreted as a url (could be relative or absolute)

    Returns
    -------
    list
        of namedtuples with
            href : string
            mb : string
                File size in MB calculated from content-length from http header
            type : string
                Unaltered from "content-type" field from http header
    """

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "http://" + url

    try:
        with contextlib.closing(urllib.request.urlopen(url)) as response:
            doc = str(response.read())
    except urllib.error.URLError:
        return []

    parser = MyHTMLParser()
    parser.feed(doc)

    hrefs = [urllib.parse.urljoin(url, href) for href in parser.hrefs]
    hrefs = [href for href in hrefs if urllib.parse.urlparse(href).scheme in ["http", "https"]]

    with multiprocessing.pool.ThreadPool(10) as thread_pool:
        links = thread_pool.map(_compose_link_info_tuple, hrefs)

    links = [link for link in links if link is not None]

    return links


def get_file_links(url, add_links_from_linked_pages=False, no_of_files_limit=None,
                   no_of_processes_specified_by_user=None, whitelist=None, blacklist=None, interactive=False):
    """
    Gets all links from a web page (and optionally the web pages linked to from it) and filters this list for
    links to files.

    Parameters
    ----------
    url : str
    add_links_from_linked_pages : bool
    no_of_files_limit : int
    whitelist : str or list
    blacklist : str or list
    interactive : bool

    Returns
    -------
    list
        A list of named tuples of the format described in the dosctring for get_links()
    """

    def check_count(count):
        """ Checks if the list of files to be downloaded has gotten too long; raises exception if the case.
        """
        if no_of_files_limit and count > int(no_of_files_limit):
            logging.critical("The user specified max limit on the number of files is set to %s, and there are at least"
                             "%s file links found. Aborting" % (no_of_files_limit, count))
            raise RuntimeError("There are more files to download than the limit specified!")

    def follow_link_check(link):
        """ Checks if a given link is to a web page from the same domain as the url parameter from the outer function
        """
        same_domain = urllib.parse.urlparse(url).netloc == urllib.parse.urlparse(link.href).netloc
        return link.type.startswith("text/html") and same_domain

    def file_link_check(link, whitelist, blacklist):
        """ Checks if a given link is to a file, and if so if the file ending is whitelisted or blacklisted.
        """
        if link.type.startswith("application") or link.type.startswith("text/plain") \
               or link.type.startswith("image") or link.type.startswith("audio") \
               or link.type.startswith("video"):

            if blacklist:
                if type(blacklist) is str:
                    blacklist = blacklist.split()
                for item in blacklist:
                    if fnmatch.fnmatch(link.href, "*." + item):
                        return False

            if whitelist:
                if type(whitelist) is str:
                    whitelist = whitelist.split()
                match = False
                for item in whitelist:
                    if fnmatch.fnmatch(link.href, "*." + item):
                        match = True
                return match

            return True

        else:
            return False

    if not (url.startswith("http://") or url.startswith("https://")):
        url = "http://" + url

    links = get_links(url)

    file_links = [link for link in links if file_link_check(link, whitelist, blacklist)]

    count = len(file_links)
    check_count(count)

    if add_links_from_linked_pages:
        if interactive:
            html_links = [link for link in links
                          if follow_link_check(link)
                          and _query_yes_no("Add files linked to from %s?" % (link.href), "yes")]
        else:
            html_links = [link for link in links if follow_link_check(link)]
        no_of_processes = _get_max_no_of_processes(no_of_processes_specified_by_user)
        logging.info("%s of %s processors will be used for further http requests (if as many are available)" % (
            no_of_processes, multiprocessing.cpu_count()))
        with multiprocessing.Pool(no_of_processes) as process_pool:
            nested_links = process_pool.map(get_links, [link.href for link in html_links])

        links_from_link = []
        for sublist in nested_links:
            for link in sublist:
                links_from_link.append(link)

        file_links_from_link = [link for link in links_from_link if file_link_check(link, whitelist, blacklist)]
        count = count + len(file_links_from_link)
        check_count(count)
        file_links.extend(file_links_from_link)

    return list(set(file_links))


def download(source, target="download", mb_per_file_limit=None, no_of_processes_specified_by_user=None,
             interactive_download_prompt=False):
    """
    Downloads files to local directory given url or list of urls.

    Parameters
    ----------
    source : str or namedtuple or list of str or namedtuple
        The namedtuples, if used, must have href and mb fields, with url in href
    target : str
        Path for which directory to download to
    mb_per_file_limit : float or None
        File size limit in MB (0 means no limit)
    no_of_processes_specified_by_user : int or None
        Used as a limit for number of simultaneously spawned processes
    interactive_download_prompt : bool
        Determines whether or not the user is to be asked about whether or not to download each file
    """

    if type(source) is not list:
        source = [source]
    if source:
        if not target == "":
            os.makedirs(target, exist_ok=True)
            target = target.rstrip("/") + "/"

        if len(source) > 10:
            no_of_processes = _get_max_no_of_processes(no_of_processes_specified_by_user)
            logging.info("%s of %s processors will be used for downloading (if as many are available)" % (
                no_of_processes, multiprocessing.cpu_count()))
        else:
            no_of_processes = 1

        link_info_tuples = []
        for link in source:

            try:
                href = link.href
                mb = link.mb
            except AttributeError:
                if type(link) is str:
                    href = link
                    mb = "?"
                else:
                    raise ValueError("Invalid input: Use urls or namedtuples in the following format:"
                                     " 'href mb type'")

            if not (href.startswith("http://") or href.startswith("https://")):
                href = "http://" + href

            if mb != "?" and mb_per_file_limit is not None and float(mb) > float(mb_per_file_limit):
                logging.warning("Skipping because file size %s MB > %s MB limit: %s" % (mb, mb_per_file_limit, href))
            else:
                target_path = target + href[href.rfind("/")+1:]
                link_info_tuples.append((href, target_path, mb))

        if interactive_download_prompt:
            link_info_tuples = [tuple for tuple in link_info_tuples
                                if _query_yes_no("Download %s?" % (tuple[0]), "yes")]

        if len(link_info_tuples) > 10:
            link_info_tuples_portions = []
            portion_size = len(link_info_tuples) // no_of_processes + 1
            for i in range(0, len(link_info_tuples), portion_size):
                link_info_tuples_portions.append(link_info_tuples[i:i + portion_size])

            with multiprocessing.Pool(no_of_processes) as process_pool:
                process_pool.map(_delegate_downloads_to_threads, link_info_tuples_portions)

        else:
            _delegate_downloads_to_threads(link_info_tuples)


def trawl(url, add_links_from_linked_pages=False, no_of_files_limit=None, no_of_processes_specified_by_user=None,
          whitelist=None, blacklist=None, target="download", mb_per_file_limit=None, quiet=False, interactive=False,
          interactive_download_prompt=False):
    """
    Gets list of file links from get_file_links and passes it to download.

    Parameters
    ----------
    url : str
    add_links_from_linked_pages : bool
    no_of_files_limit : int or None
    no_of_processes_specified_by_user : int or None
    whitelist : str or list
    blacklist : str or list
    target : str
    mb_per_file_limit : float or None
    quiet : bool
    interactive : bool
    interactive_download_prompt : bool
    """

    logging.basicConfig(level=logging.CRITICAL if quiet else logging.INFO,
                        format="%(levelname)s (%(asctime)s): %(message)s", datefmt="%H:%M:%S")
    file_links = get_file_links(url, add_links_from_linked_pages=add_links_from_linked_pages,
                                no_of_files_limit=no_of_files_limit,
                                no_of_processes_specified_by_user=no_of_processes_specified_by_user,
                                whitelist=whitelist, blacklist=blacklist, interactive=interactive)
    logging.info("%s files to download in total" % (len(file_links)))
    download(file_links, target=target, mb_per_file_limit=mb_per_file_limit,
             no_of_processes_specified_by_user=no_of_processes_specified_by_user,
             interactive_download_prompt=interactive_download_prompt)


def main():
    """ Entry point for command line users.
    """
    args = _parse_args()

    trawl(args.url, add_links_from_linked_pages=args.add_links_from_linked_pages,
          no_of_files_limit=args.no_of_files_limit,
          no_of_processes_specified_by_user=args.processes, whitelist=args.whitelist, blacklist=args.blacklist,
          target=args.target, mb_per_file_limit=args.mb_per_file_limit, quiet=args.quiet, interactive=args.interactive,
          interactive_download_prompt=args.interactive_download_prompt)


if __name__ == "__main__":
    main()
