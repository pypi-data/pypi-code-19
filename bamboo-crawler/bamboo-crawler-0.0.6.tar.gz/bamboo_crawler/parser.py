from collections import OrderedDict
from contextlib import closing
import io

import jinja2
from yaml.dumper import Dumper
from yaml.loader import SafeLoader
from yaml.resolver import BaseResolver


def parse_ordered_yaml(infile):
    def ordering(loader, node):
        return OrderedDict(loader.construct_pairs(node))
    loader = SafeLoader(infile)
    try:
        tag = BaseResolver.DEFAULT_MAPPING_TAG
        loader.add_constructor(tag, ordering)
        return loader.get_single_data()
    finally:
        loader.dispose()


def ordered_dump(doc):
    s = io.StringIO()

    def ordering(dumper, doc):
        tag = BaseResolver.DEFAULT_MAPPING_TAG
        return dumper.represent_mapping(tag, doc.items())

    dumper = Dumper(s, default_flow_style=False)
    dumper.add_representer(OrderedDict, ordering)
    dumper.open()
    with closing(dumper):
        dumper.represent(doc)
    return s.getvalue()


def parse_recipe(infile, config):
    source = infile.read()
    template = jinja2.Template(source)
    rendered_source = template.render(**config)
    recipe = parse_ordered_yaml(rendered_source)
    return recipe
