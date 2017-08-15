# -*- coding: utf-8 -*-

"""
The MIT License (MIT)

Copyright (c) 2017 Datmellow

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
from league.enums import Regions
from league.riotDTO import RiotDto

class Shard(RiotDto):
    """Represents a League Shard

    Attributes
    ----------
    name : str
        The name of the region
    region : :class:`Union`[:class:`Regions`,str]
        The region the shard belongs to
    hostname : str
        the server hostname of the shard
    services : list[:class:`Service`]
        list of all services
    slug : str
        The shorthand of the region


    """

    def __init__(self, **kwargs):
        super(Shard, self).__init__(**kwargs)
        self.name = kwargs.get('name')
        try:
            self.region = Regions[kwargs.get('region_tag')]
        except KeyError:
            self.region = kwargs.get('region_tag')
        self.hostname = kwargs.get('hostname')
        self.services = [Service(**data) for data in kwargs.get('services')]
        self.slug = kwargs.get('slug')


class Service:
    """Represents a service

    Attributes
    ----------
    online : bool
        displays the current status of the service, True = online
    incidents : list[:class:`Incident`]
        Shows all incidents for this service, can be empty if nothing is wrong
    name: str
        the name of the service


    """

    def __init__(self, **kwargs):
        self.online = True if kwargs.get('status').lower() == "online" else False
        self.incidents = [Incident(**data) for data in kwargs.get('incidents')]
        self.name = kwargs.get('name')


class Incident:
    """Represents an Incident

    Attributes
    ----------
    active : bool
        shows if the incident is still active
    created : str
        displays when the incident was filed
    id : long
        the id of the incident
    updates : list[:class:`Message`]
        all the updates for this incident, newest is always first


    """

    def __init__(self, **kwargs):
        self.active = kwargs.get('active')
        self.created = kwargs.get('created_at')
        self.id = kwargs.get('id')
        self.updates = [Message(**data) for data in kwargs.get('updates')]


class Message:
    """Represents a incident message

    Attributes
    ----------
    severity : str
        The severity of the message
    author : str
        who posted the message
    created_at : str
        when the message was posted
    translations : list[dict]
        like of any possible translations
    updated_at : str
        When the message was last updated
    content : str
        the content of the message
    id : str
        the id of the message

    """

    def __init__(self, **kwargs):
        self.severity = kwargs.get('severity')
        self.author = kwargs.get('author')
        self.created_at = kwargs.get('created_at')
        self.translations = kwargs.get('translations')
        self.updated_at = kwargs.get('updated_at')
        self.content = kwargs.get('content')
        self.id = kwargs.get('id')
