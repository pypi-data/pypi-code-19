# -*- coding: utf-8 -*-
from geolink_formatter.entity import Msg
from geolink_formatter.format import HTML
from geolink_formatter.parser import XML

__version__ = '1.0.0'


class GeoLinkFormatter(object):
    def __init__(self, host_url=None, dtd_validation=False):
        """Creates a new GeoLinkFormatter instance.

        Args:
            host_url (str): URL of the ÖREBlex host to resolve relative URLs. The complete URL until but
                without the */api* part has to be set, starting with *http://* or *https://*.
            dtd_validation (bool): Enable/disable validation of document type definition (DTD).
                Optional, defaults to False.

        """
        self.__host_url__ = host_url
        self.__dtd_validation__ = dtd_validation

    def html(self, source):
        """Returns the HTML representation of the geoLink XML form the specified source.

        Args:
            source (str or unicode): The geoLink source. Can be a XML string or an URL to load the XML via
                HTTP/HTTPS request.

        Returns:
            str: An HTML formatted string containing the documents as HTML list.

        Raises:
            TypeError: Raised on invalid source type.
            lxml.etree.XMLSyntaxError: Raised on failed validation.
            requests.HTTPError: Raised on failed HTTP request.

        """
        parser = XML(host_url=self.__host_url__, dtd_validation=self.__dtd_validation__)
        if isinstance(source, (str, unicode)):
            if source.startswith('http://') or source.startswith('https://'):
                return HTML().format(parser.from_url(source))
            else:
                return HTML().format(parser.from_string(source))
        else:
            raise TypeError(Msg.invalid_argument.format(
                arg='source',
                expected=(str, unicode),
                got=source.__class__
            ))
