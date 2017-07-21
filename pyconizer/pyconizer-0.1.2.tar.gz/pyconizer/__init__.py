# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import base64
import os
import shutil

from pyconizer.lib.api.image import download_legend_icon
from pyconizer.lib.api.sld import load_sld_content, extract_rules
from pyconizer.lib.api.structure import Configuration, write, read, persist_layer_path, persist_mapping, \
    write_rule_to_image_icon, write_rule_to_svg_icon


def create_icons_from_scratch(configuration, path, file_name='mapping.json', images=False, svgs=False):
    """
    This is probably the starting point. If you use this package for the first time you might want use this.

    Args:
        configuration (list of dict): The minimal configuration to construct all images from scratch
        path (str): The root path where all the stuff will be created in.
        file_name (str): The name of the file which is used to save the configuration in. The files mime
            type is always json. The only thing you can change is the name if you don't like the name
            'mapping.json'.
        images (bool): Switch to create also icon image files.
        svgs (bool): Switch to create also icon svg files.
    """

    configuration = Configuration.from_dict(configuration)
    for layer in configuration.layers:

        # download the sld content and store it to the config object
        sld_content = load_sld_content(layer.get_styles_url)
        layer.get_styles.set_content(sld_content)

        # add the empty structure of rules extracted from the SLD
        named_layers = extract_rules(sld_content)
        layer.get_legend.add_named_layers(named_layers)
        layer.get_legend.create_rule_urls(layer.url)
    write(path, configuration, file_name=file_name, images=images, svgs=svgs)


def update_icon_content_by_layer_name(path, layer_name, mapping_file_name='mapping.json', images=False,
                                      svgs=False):
    """
    This function updates all icon contents in an existing structure. The update is filtered by the
    layer_name to update only the wanted layer.

    Args:
        path (str): The root path which all the files will be created in.
        layer_name (str): This must be the layer name fitting one of the names in the JSON configuration. It
            must not be the name of some named layer.
        mapping_file_name (str): The name of the mapping file which is expected to be existing inside of the
            path.
        images (bool): Switch to create also icon image files.
        svgs (bool): Switch to create also icon svg files.
    """

    configuration = read(os.path.abspath('{path}/{mapping}'.format(path=path, mapping=mapping_file_name)))
    found_layer = None
    for index, layer in enumerate(configuration.layers):
        if layer.name == layer_name:
            print('found the layer to update:', layer.name)
            found_layer = layer
    if found_layer:
        # download the sld content and store it to the config object
        sld_content = load_sld_content(found_layer.get_styles_url)
        found_layer.get_styles.set_content(sld_content)

        # add the empty structure of rules extracted from the SLD
        named_layers = extract_rules(sld_content)

        # remove layer from configuration before add a new one
        found_layer.get_legend.set_named_layers(named_layers)
        found_layer.get_legend.create_rule_urls(found_layer.url)
        if images or svgs:
            shutil.rmtree(os.path.abspath('{path}/{layer}'.format(path=path, layer=layer_name)))
        for named_layer in found_layer.get_legend.named_layers:
            persist_layer_path(path, layer_name, named_layer.name)
            for rule in named_layer.rules:
                download_legend_icon(rule)
                combined_path = persist_layer_path(path, found_layer.name, named_layer.name)
                if images:
                    write_rule_to_image_icon(combined_path, rule)
                if svgs:
                    write_rule_to_svg_icon(combined_path, rule)
        persist_mapping(path, configuration)
    else:
        print('No layer with name "{0}" was found'.format(layer_name))


def delete_from_structure_by_layer_name(path, layer_name, mapping_file_name='mapping.json', images=False,
                                        svgs=False):
    """
    Deletes a layer from the structure. If the json_only parameter is set to False, it is done also in the
    structures file system representation.

    Args:
        path (str): The root path which all the files will be created in.
        layer_name (str): This must be the layer name fitting one of the names in the JSON configuration. It
            must not be the name of some named layer.
        mapping_file_name (str): The name of the mapping file which is expected to be existing inside of the
            path.
        images (bool): Switch to create also icon image files.
        svgs (bool): Switch to create also icon svg files.
    """

    configuration = read(os.path.abspath('{path}/{mapping}'.format(path=path, mapping=mapping_file_name)))
    found_layer_index = None
    for index, layer in enumerate(configuration.layers):
        if layer.name == layer_name:
            found_layer_index = index
    if found_layer_index is not None:
        configuration.layers.pop(found_layer_index)
        if images or svgs:
            shutil.rmtree(os.path.abspath('{path}/{layer}'.format(path=path, layer=layer_name)))
        persist_mapping(path, configuration)
    else:
        print('No layer with name "{0}" was found'.format(layer_name))


def get_icon(path, layer_name, class_name, mapping_file_name='mapping.json'):
    """

    Args:
        path (str): The root path which all the files will be created in.
        layer_name (str): This must be the layer name fitting one of the names in the JSON configuration. It
            must not be the name of some named layer.
        class_name (unicode): The class name which is used to extract the icon.
        mapping_file_name (str): The name of the mapping file which is expected to be existing inside of the
            path.

    Returns:
        str: The content of the icon. It is encoded as base code 64.
    """
    configuration = read(os.path.abspath('{path}/{mapping}'.format(path=path, mapping=mapping_file_name)))
    for layer in configuration.layers:
        if layer.name == layer_name:
            print('found the layer you where looking for:', layer.name)
            for named_layer in layer.get_legend.named_layers:
                for rule in named_layer.rules:
                    if rule.class_name == class_name:
                        print('found the rule you where looking for:', class_name)
                        return base64.b64encode(rule.content)
