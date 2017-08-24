# -*- coding: utf-8 -*-

import json
import six

from cliff import command
from cliff import lister
from cliff import show

from registryctl.catalog import client

class CatalogList(lister.Lister):
    def get_parser(self, prog_name):
        parser = super(CatalogList, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        columns = ('repository','tags')
        req_list = client.CatalogClient(self.app.client).catalogList()
        return (columns, req_list)

class CatalogShow(show.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CatalogShow, self).get_parser(prog_name)
        parser.add_argument('repository')
        parser.add_argument('tag', nargs='?', default='latest')
        return parser

    def take_action(self, args):
        req_show = client.CatalogClient(self.app.client).catalogShow(args.repository, args.tag)
        return self.dict2columns(req_show)

class CatalogDelete(show.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CatalogDelete, self).get_parser(prog_name)
        parser.add_argument('repository')
        parser.add_argument('tag')
        return parser

    def take_action(self, args):
        req_delete = client.CatalogClient(self.app.client).catalogDelete(args.repository, args.tag)
        return self.dict2columns(req_delete)
