# -*- coding: utf-8 -*-

import json

from cliff import command
from cliff import lister
from cliff import show
import six


def _columnize_list(columns, list):
    items = []
    for item in list:
        d = []
        for c in columns:
            d.append(item[c])
        items.append(d)

    return (columns, items)


class CatalogList(lister.Lister):
    def get_parser(self, prog_name):
        parser = super(CatalogList, self).get_parser(prog_name)
        return parser

    def take_action(self, args):
        columns = ('repository','tags')
        req_list = self.app.client.catalogList()
        return (columns, req_list)

class CatalogShow(show.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CatalogShow, self).get_parser(prog_name)
        parser.add_argument('repository')
        parser.add_argument('tag', nargs='?', default='latest')
        return parser

    def take_action(self, args):
        req_show = self.app.client.catalogShow(args.repository, args.tag)
        return self.dict2columns(req_show)

class CatalogDelete(show.ShowOne):
    def get_parser(self, prog_name):
        parser = super(CatalogDelete, self).get_parser(prog_name)
        parser.add_argument('repository')
        parser.add_argument('tag')
        return parser

    def take_action(self, args):
        req_delete = self.app.client.catalogDelete(args.repository, args.tag)
        return self.dict2columns(req_delete)
