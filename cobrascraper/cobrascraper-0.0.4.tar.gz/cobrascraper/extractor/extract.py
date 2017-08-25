# -*- coding: utf-8 -*-
from lxml import html
from lxml.etree import tostring
from lxml.etree import ParserError
from lxml.html.clean import Cleaner
import logging

logger = logging.getLogger(__name__)


def extract(html, definition, metadata={}):
    """Loops through the definitions and extract the fields

    Args:
        html (str): Full html of the page
        definition (dict): Field names and how to select them

    Keyword Args:
        metadata (dict): User defined data to be returned with the raw data under the key `metadata`

    Returns:
        dict: Contains all the field names with their contents, metadata is added as a key if passed in

    """
    rdata = {}
    dom = _convert_source(html)

    if metadata:
        rdata['metadata'] = metadata

    rdata.update(_parse_definition(dom, definition))

    return rdata


def _parse_definition(dom, definition):
    """Pare each sibling in a definition

    Args:
        dom (lxml.html.HtmlElement): dom element to be parsed
        definition (dict): definition of the definition to be collected

    Returns:
        dict: Key being the field name

    """
    results = {}
    for field in definition:
        field_values = _parse_field_values(dom, field)
        results.update(field_values)

    return results


def _parse_field_values(dom, definition):
    """Recursive function that uses the definition to return the required data

    Args:
        dom (lxml.html.HtmlElement): dom element to be parsed
        definition (dict): definition of the definition to be collected

    Returns:
        dict | list: dict|list of dicts

    """
    name = definition['name']
    children = definition.get('children', [])
    has_multiple = definition.get('has_multiple', False)
    get_rank = definition.get('rank', False)
    get_contents = definition.get('content', True)
    result = {}

    selector = _get_selector(definition)
    selector_results = dom.cssselect(selector)

    if len(selector_results) == 0:
        return {}

    if has_multiple is False:
        selector_results = [selector_results[0]]
        result[name] = {}
    else:
        result[name] = []

    for rank, result_dom in enumerate(selector_results, start=1):
        element_result = {}

        # Add Rank
        if has_multiple is True and get_rank is True:
            element_result['rank'] = rank

        # Add Attrs
        if definition.get('attrs'):
            for attr_name, attr_value in _get_element_attrs(result_dom, definition.get('attrs')).items():
                result[name + '_attr_' + attr_name] = attr_value

        # Get raw html as string
        if definition.get('raw'):
            result[name + '_raw'] = _get_element_content_raw(result_dom)

        # Get content for field
        if children:  # Dig deeper and get child data
            # If current selector is blank, then pass the html result of the parent defination, not of the result
            if not definition.get('selector', ''):
                result_dom = dom
            element_result.update(_parse_definition(result_dom, children))
        elif get_contents:
            # Get the contents of the element
            element_result = _get_element_content(result_dom)

        # Return single item or list of items
        if has_multiple is True:
            result[name].append(element_result)
        else:
            result[name] = element_result

    return result


def _get_selector(definition):
    """Get selector from current definition or build from children
    TODO: Do I really want to do it this way???
          Or how to handle looping through the results better to get the overall rank
    """
    selector = definition.get('selector', '')

    if not selector:
        # Need to build from children
        # TODO: Find a test that will need to build from a few children deep
        selectors = []
        for child in definition.get('children', []):
            # Might need to go deeper here if needed
            selectors.append(child.get('selector'))

        selector = ','.join(selectors)

    return selector


def _get_element_attrs(element, attrs):
    """Get the value of an attribute from an element

    Args:
        element (lxml.html.HtmlElement): dom element to be parsed
        attrs (list): Attributes to check

    Returns:
        dict: keys being the name of the attribute

    """
    result = {}

    for attr in attrs:
        result[attr] = element.get(attr)

    return result


def _get_element_content_raw(element):
    """ Get the whole element as a string

    Args:
        element (lxml.html.HtmlElement): dom element to be parsed

    Returns:
        str: html as a string

    """
    # lxml.etree.tostring
    return tostring(element).decode("utf-8")


def _get_element_content(element):
    """ Get all text from element and its children as an list (if multiple elements, else string)

    Args:
        element (lxml.html.HtmlElement): dom element to be parsed

    Returns:
        str: All text found in element

    """
    return element.text_content()


def _convert_source(html_source):
    """Convert string to lxml.html.HtmlElement

    Args:
        html_source (str): String of html to convert

    Returns:
        lxml.html.HtmlElement: To make it parsable

    """
    parser = html.HTMLParser(encoding='utf-8')
    try:
        clean_content = Cleaner(safe_attrs_only=False).clean_html(html_source)
    except ParserError:
        logger.exception("Error parsing html")
        clean_content = '<div></div>'

    dom = html.document_fromstring(clean_content, parser=parser)
    dom.resolve_base_href()

    return dom
