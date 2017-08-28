from pyadf.inline_nodes.text import Text
from pyadf.inline_nodes.emoji import Emoji
from pyadf.inline_nodes.mention import Mention

from pyadf.inline_nodes.marks.link import Link

class GroupNode(object):

    def __init__(self, parent=None):
        self.content = []
        self.parent = parent
        pass

    def to_doc(self):
        attrs = self.attrs()
        
        result = {
            'type': self.type,
            'content': [f.to_doc() for f in self.content]
        }

        if (attrs != None):
            result['attrs'] = attrs

        return result

    def attrs(self):
        return None

    def text(self, text):
        node = Text(text)
        self.content.append(node)
        return self

    def emoji(self, shortname, emoji_id=None, fallback=None):
        node = Emoji(shortname, emoji_id=emoji_id, fallback=fallback)
        self.content.append(node)
        return self

    def mention(self, mention_id, mention_text, access_level=None):
        node = Mention(mention_id, mention_text, access_level=access_level)
        self.content.append(node)
        return self

    def end(self):
        return self.parent

    # these marks apply to the last-used inline node
    def link(self, href, title=None):
        if (self.content == None or len(self.content) == 0):
            raise ValueError('Can\'t apply marks when there is no content to mark.')
        node = Link(href, title)
        self.content[-1].add_mark(node)
        return self