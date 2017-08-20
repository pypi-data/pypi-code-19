# -*- coding: utf-8 -*-

import requests

from registryctl.exceptions import *

class RegistryCtlClient(object):

      def __init__(self, url, auth=None):
          self._url = url
          self._session = requests.Session()
          self._basic_auth = auth
          self._header_v2 = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}

      def _get(self, url):
          return self._session.get(url=url,auth=self._basic_auth)

      def _head(self, url, header):
          req_head = self._session.head(url=url,
                                        auth=self._basic_auth,
                                        headers=self._header_v2)
          if req_head.status_code == 404:
              raise NotFoundException()
          return req_head.headers[header]

      def _get_repository_tags(self,repository):
          url = '%s/%s/tags/list' % (self._url, repository)
          return self._get(url).json()['tags']

      def _get_digest(self, repository, tag):
          url = '%s/%s/manifests/%s' % (self._url, repository, tag)
          try:
            return self._head(url,'Docker-Content-Digest')
          except NotFoundException:
            raise TagNotFoundException('Tag "%s" not found' % tag)

      def _delete(self, url):
          return self._session.delete(url=url,auth=self._basic_auth)

      def catalogList(self):
          url = '%s/_catalog' % (self._url)
          repositories = self._get(url).json()['repositories']
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
            url = '%s/%s/manifests/%s' % (self._url, repository, digest)
            res_delete.update({'tag': tag, 'digest': digest})
          except TagNotFoundException as tnfe:
            res_delete.update({'error': str(tnfe)})
            return res_delete

          req_delete = self._delete(url)

          if req_delete.status_code != 202:
            print(req_delete.status_code)
            res_delete.update({'error': 'delete error'})
          else:
            res_delete.update({'delete': 'ok'})
          return res_delete
