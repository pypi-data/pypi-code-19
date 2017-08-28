#! /usr/bin/python3
# -*- coding: utf-8 -*-

from pyadf.paragraph import Paragraph

class Document(object):

    def __init__(self):
        self.content = []
        pass

    def to_doc(self):
        return {
            'version': 1,
            'type': 'doc',
            'content': [
                x.to_doc() for x in self.content
            ]
        }

    def paragraph(self):
      p = Paragraph(self)
      self.content.append(p)
      return p