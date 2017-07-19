# -*- coding: utf-8 -*-
"""
.. module:: scriptler.yaml
   :platform: Unix
   :synopsis: TODO.

.. moduleauthor:: Aljosha Friemann a.friemann@automate.wtf

----------------------------------------------------------------------------
"THE BEER-WARE LICENSE" (Revision 42):
<aljosha.friemann@gmail.com> wrote this file.  As long as you retain this
notice you can do whatever you want with this stuff. If we meet some day,
and you think this stuff is worth it, you can buy me a beer in return.
----------------------------------------------------------------------------

"""

import re, ruamel.yaml as yaml

from scriptler.model import Source, Script, Config

def _represent_model(t):
    def represent_subclass(dumper, data):
        return dumper.represent_mapping(data.__class__.__name__, dict(data))
    return represent_subclass

yaml.add_representer(Source, _represent_model(Source))
yaml.add_representer(Script, _represent_model(Script))
yaml.add_representer(Config, _represent_model(Config))

def load(stream):
    return yaml.safe_load(stream)

def dump(dictionary, indent=2):
    dump = yaml.dump(dictionary, indent=indent, default_flow_style=False)
    dump = re.sub(r'!<.*>', '', dump)

    return dump.strip()
