from ftw.simplelayout.browser.blocks.base import BaseBlock
from plone import api
from urlparse import urlparse


class IFrameBlockView(BaseBlock):
    def __call__(self):
        return self.index()

    def can_add(self):
        return api.user.has_permission('ftw.iframeblock: Add iFrame block')

    def get_url(self):
        url = self.request.get('i_{}'.format(self.context.getId()),
                               self.request.get('i', None))
        if url and self.is_valid_url(url):
            return url
        else:
            return self.context.url

    def is_valid_url(self, url):
        url = urlparse(url)
        if not url.netloc:
            # URL is not fully qualified
            return False

        if url.scheme not in ('http', 'https'):
            # URL is not http
            return False

        standard_url = urlparse(self.context.url)
        if url.netloc != standard_url.netloc:
            # Different domain
            return False

        return True
