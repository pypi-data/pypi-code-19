# -*- coding: utf-8 -*-
"""
.. module:: scriptler.model
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

from simple_model import Model, Attribute, list_type

class Source(Model):
    __hide_unset__ = True
    name = Attribute(str)
    url = Attribute(str)
    user = Attribute(str, optional=True)
    password = Attribute(str, optional=True)
    branch = Attribute(str, optional=True)

class Script(Model):
    __hide_unset__ = True
    name = Attribute(str)
    path   = Attribute(str)
    source = Attribute(str, optional=True)
    command = Attribute(str, optional=True)

def parse_entries(t):
    def parse(d):
        result = {}
        for name, values in d.items():
            result.update({ name: t(**values) })
        return result

    return parse

class Config(Model):
    __hide_unset__ = True
    path       = Attribute(str)
    script_dir = Attribute(str)
    scripts    = Attribute(list_type(Script), fallback=[])
    sources    = Attribute(list_type(Source), fallback=[])

# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4 fenc=utf-8
