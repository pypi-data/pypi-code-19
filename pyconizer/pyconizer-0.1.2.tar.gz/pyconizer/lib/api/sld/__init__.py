# -*- coding: utf-8 -*-
import xml.etree.ElementTree as etree
from pyconizer.lib.api.structure import Rule, NamedLayer
from pyconizer.lib.api.svg import create_svg_icon

# python 3 compatibility
from future.moves.urllib.request import urlopen
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


def FactoryFromString(sld_content):
    """

    Args:
        sld_content (str): The content of an SLD to check for version and parse with the found module.

    Returns:
        pyconizer.lib.api.sld.v1_0_0.classes.StyledLayerDescriptor: The complete objectified representation
            of the SLD.
    """
    parser = etree.XMLParser()
    tree = etree.fromstring(sld_content, parser)
    version = tree.attrib.get('version')
    if version == '1.0.0':
        from pyconizer.lib.api.sld.v1_0_0 import classes
        found_version = classes
    else:
        raise LookupError('Version is not supported. Version of SLD was: {0}'.format(version))
    output = StringIO(sld_content)
    parsed_sld = found_version.parse(output, parser)
    return parsed_sld


# def Factory(sld_file_path):
#     """
#
#     Args:
#         sld_file_path (str): The SLD file to check for version and parse with the found module.
#
#     Returns:
#         pyconizer.lib.api.sld.v1_0_0.classes.StyledLayerDescriptor: The complete objectified representation
#             of the SLD.
#     """
#     content = open(sld_file_path).read()
#     return FactoryFromString(content)


def check_xml_version(sld_content):
    """
    Small check for xml definition in first line of SLD xml content. For convenience reason we should use
    this method to provide a correct xml for further processing.

    Args:
        sld_content (str): The xml string which should be checked for the magic first xml tag.

    Returns:
        str: The maybe updated xml string.

    """
    if not str().startswith('<?xml '):
        sld_content = '<?xml version="1.0" encoding="UTF-8" ?>\n{0}'.format(sld_content)
    return sld_content


def load_sld_content(url):
    """
    Load the SLD from the passed url.

    Args:
        url (str): The URL which should return a SLD generated from WMS.

    Returns:
        str: The SLD as XML in a simple string.

    """
    response = urlopen(url)
    return check_xml_version(response.read())


def extract_rules(sld_content):
    """
    Extract all Rules with its name and classes.

    Args:
        sld_content (str): The SLD you want to split up in all its svg symbol definitions.

    Returns:
        list of pyconizer.lib.api.structure.NamedLayer: A list of named layers and their image
            configs all wrapped in application structure.
    """
    sld_content = FactoryFromString(sld_content)
    layers = []
    for named_layer in sld_content.NamedLayer:
        named_layer_name = named_layer.Name
        rules = []
        for user_style in named_layer.UserStyle:
            for feature_type_style in user_style.FeatureTypeStyle:
                for rule in feature_type_style.Rule:
                    # only comparison ops are supported now, if rule has no filter => What is this????
                    if not rule.Filter and rule.Name:
                        structure_rule = Rule(class_name=rule.Name)
                        structure_rule.set_svg(create_svg_icon(rule.Symbolizer))
                        rules.append(structure_rule)
                    elif rule.Filter and not rule.Name:
                        structure_rule = Rule(
                            filter_class=rule.Filter.comparisonOps.expression[1].get_valueOf_()
                        )
                        structure_rule.set_svg(create_svg_icon(rule.Symbolizer))
                        rules.append(structure_rule)
                    elif rule.Filter and rule.Name:
                        structure_rule = Rule(
                            class_name=rule.Name,
                            filter_class=rule.Filter.comparisonOps.expression[1].get_valueOf_()
                        )
                        structure_rule.set_svg(create_svg_icon(rule.Symbolizer))
                        rules.append(structure_rule)
        layers.append(NamedLayer(name=named_layer_name, rules=rules))
    return layers
