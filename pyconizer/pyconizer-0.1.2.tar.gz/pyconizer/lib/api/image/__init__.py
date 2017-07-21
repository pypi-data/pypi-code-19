# -*- coding: utf-8 -*-
import imghdr
import uuid
from future.moves.urllib.request import urlopen


def set_file_name(rule):
    """
    Create a filename depending on the content (mime type). If a name is existent already, it will be reused.
    It might have some changes in the mime type of the content. This mime type will be changed if necessary.

    Args:
        rule (pyconizer.lib.api.structure.Rule): The rule to which the file name should be applied.
    """
    if rule.file_name:
        print('use old file name')
        unique = rule.file_name.split('.')[0]
    else:
        print('create new file name')
        unique = uuid.uuid4()
    rule.set_file_name('{file_name}.{mime_type}'.format(
        file_name=unique,
        mime_type=imghdr.what(None, h=rule.content)
    ))


def download_legend_icon(rule):
    """
    Downloads the content of the icon from the url.

    Args:
        rule (pyconizer.lib.api.structure.Rule): The rule which icon should be downloaded.

    """
    if rule.rule_url:
        print('process rule:', rule.class_name)
        print(rule.rule_url)
        response = urlopen(rule.rule_url)
        rule.set_content(response.read())
        set_file_name(rule)
    else:
        print('no url was found on rule with class name:', rule.dict)


def download_all_legend_icons(configuration):
    """
    Load images via configured get styles request and prepared and parsed sld content
    Args:
        configuration (pyconizer.lib.api.structure.Configuration): The configuration which holds all
            information to download the icons.

    Returns:
        list of dict: The Updated config dictionary containing now the obtained images.
    """
    for layer in configuration.layers:
        print('process layer:', layer.name)
        for named_layer in layer.get_legend.named_layers:
            print('process named layer:', named_layer.name)
            for rule in named_layer.rules:
                download_legend_icon(rule)
