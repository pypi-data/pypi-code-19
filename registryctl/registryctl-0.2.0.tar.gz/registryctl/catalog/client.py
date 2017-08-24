# -*- coding: utf-8 -*-

import requests

from registryctl.common.exceptions import *
from registryctl.common import authclient

class CatalogClient(object):
      def __init__(self, _authclient):
          self.authclient = _authclient

      def _get_repository_tags(self,repository):
          url = '%s/%s/tags/list' % (self.authclient._url, repository)
          return self.authclient._get(url).json()['tags']

      def _get_digest(self, repository, tag):
          url = '%s/%s/manifests/%s' % (self.authclient._url, repository, tag)
          try:
            return self.authclient._head(url,'Docker-Content-Digest')
          except NotFoundException:
            raise TagNotFoundException('Tag "%s" not found' % tag)

      def catalogList(self):
          url = '%s/_catalog' % (self.authclient._url)
          repositories = self.authclient._get(url).json()['repositories']
          return ((repo, self._get_repository_tags(repo)) for repo in repositories)

      def catalogShow(self, repository, tag):
          res_show = {'repository': repository}
          try:
            digest = self._get_digest(repository,tag)
            res_show.update({'tag': tag, 'digest': digest})
          except TagNotFoundException as tnfe:
            res_show.update({'error': str(tnfe)})
          return res_show

      def catalogDelete(self, repository, tag):
          res_delete = {'repository': repository}
          try:
            digest = self._get_digest(repository,tag)
            url = '%s/%s/manifests/%s' % (self.authclient._url, repository, digest)
            res_delete.update({'tag': tag, 'digest': digest})
          except TagNotFoundException as tnfe:
            res_delete.update({'error': str(tnfe)})
            return res_delete

          req_delete = self.authclient._delete(url)

          if req_delete.status_code != 202:
            print(req_delete.status_code)
            res_delete.update({'error': 'delete error'})
          else:
            res_delete.update({'delete': 'ok'})
          return res_delete
