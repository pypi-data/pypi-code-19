#!/usr/bin/python
# -*- coding: utf-8 -*-
"""XML Overrider.

Usage:
  xml-overrider --input-dir INPUT --output-dir OUTPUT --config-file CONFIG
  xml-overrider (-h | --help)
  xml-overrider --version

Options:
  -h --help                            Show this screen.
  --version                            Show version.
  --input-dir INPUT, -i INPUT          Input directory.
  --output-dir OUTPUT, -o OUTPUT       Output directory.
  --config-file CONFIG, -c CONFIG      Config file.

"""
from __future__ import unicode_literals

import os
import re

import yaml
from docopt import docopt
from lxml import etree

from xml_overrider import __version__

regexp = re.compile(r'(.*)\[([^]]*)\]')


def get_element(element):
    groups = regexp.match(element)
    attr = None
    attr_value = None

    if groups:
        element = groups.groups()[0]

        attr_value = groups.groups()[1].split("=")

        attr = str(groups.groups()[1].split("=")[0]).replace("@", "")
        attr_value = str(attr_value[-1]).replace("'", "")

    new_element = etree.Element(element)

    if attr:
        new_element.set(attr, attr_value)

    return new_element


def add(root, xpath, value):

    xpaths = xpath.split('/')

    curr_path = ""
    parent = root

    # TODO: it could be done in the contrary, and this would be really better.
    for _xpath in xpaths:
        curr_path = os.path.join(curr_path, _xpath)

        element = root.find(curr_path)

        if element is None:
            print("Adding new node {}".format(curr_path))
            element = get_element(_xpath)
            parent.append(element)
        else:
            print("Evaluating {}".format(curr_path))

        parent = element

    leaf = root.find(xpath)
    leaf.text = value


def patch(lang, values, output_dir, input_dir):

    filename = lang + ".xml"

    original_file = os.path.join(input_dir, filename)

    if os.path.isfile(original_file):
        print("-"*30)
        print("Patching {}".format(original_file))

        parser = etree.XMLParser()
        original_file = etree.parse(original_file, parser)
        root = original_file.getroot()

        for value in values:
            elem = root.find(value['xpath'])

            if elem is not None:
                print("Replacing {}/{} with {}".format(
                    value['xpath'], elem.text, value['value']))
                elem.text = value['value']
            else:
                add(root, value['xpath'], value['value'])

        etree.ElementTree(root).write(
            os.path.join(output_dir, filename), pretty_print=True, encoding='utf-8')

    else:
        print("File {} not found in {}".format(filename, input_dir))

    print("\n")


def overrider():
    arguments = docopt(__doc__, version='XML Overrider {}'.format(__version__))

    output_dir = os.path.abspath(arguments['--output-dir'])
    input_dir = os.path.abspath(arguments['--input-dir'])
    config_file = os.path.abspath(arguments['--config-file'])

    if not os.path.exists(input_dir):
        print("Invalid path {}".format(input_dir))
        exit(0)

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    with open(config_file) as yaml_file:
        config = None
        try:
            config = yaml.load(yaml_file)
        except yaml.YAMLError as exc:
            print(exc)
            exit(1)

    for _lang, _values in config['files'].items():
        patch(_lang, _values, output_dir, input_dir)

if __name__ == "__main__":
    overrider()
