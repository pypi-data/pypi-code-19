from web_wrapper import DriverRequests


def download():
    raise NotImplementedError


def save_source(url, headers={}, proxy=None, file_location=None):
    """Save the html source to file. Creates a tmp named file if no path is passed in

    Args:
        url (str): Url to be hit

    Keyword Args:
        headers (dict): Headers to set in the web driver
        proxy (str): Url including any auth as a string

    Returns:
        str: Absolute path of the saved html

    """
    raise NotImplementedError
    # source_html = get_source(url, headers=headers, proxy=proxy)
    # TODO: Save contents to tmp file and return


def get_source(url, headers={}, proxy=None):
    """Get the raw source of the url as a string

    Args:
        url (str): Url to be hit

    Keyword Args:
        headers (dict): Headers to set in the web driver
        proxy (str): Url including any auth as a string

    Returns:
        str: Html content

    """
    web = DriverRequests(proxy=proxy, headers=headers)
    raw_source = web.get_site(url, page_format='raw')

    return raw_source
