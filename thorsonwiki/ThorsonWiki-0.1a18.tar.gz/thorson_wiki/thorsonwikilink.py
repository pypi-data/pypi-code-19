import re

from django.core.urlresolvers import reverse
from django.utils.text import slugify
from markdown.extensions import Extension
from markdown.inlinepatterns import Pattern
from markdown.util import etree

def build_url(label, namespace_):
    """
    Build a URL from the label and namespace. The base and end are
    automatically added by Django.
    """

    if ':' in label:
        namespace_, label = label.split(':', 1)

    return reverse(namespace_ + ':article',
            kwargs={'slug': slugify(label)})

class ThorsonWikiLinkExtension(Extension):

    ARTICLE_NAME = r"(?P<article_name>[^\[\]]+?)"

    LINK_TEXT = r"(?:\|(?P<link_text>[^\[\]]+))?"

    WIKILINK_RE = '\[\[' + ARTICLE_NAME + LINK_TEXT + '\]\]'

    def __init__(self, *args, **kwargs):
        self.config = {
            'base_url': ['/', 'String to append to beginning or URL.'],
            'end_url': ['/', 'String to append to end of URL.'],
            'html_class': ['wikilink', 'CSS hook. Leave blank for none.'],
            'build_url': [build_url, 'Callable formats URL from label.'],
        }

        super(ThorsonWikiLinkExtension, self).__init__(*args, **kwargs)

    def extendMarkdown(self, md, md_globals):
        self.md = md

        # append to end of inline patterns
        wikilinkPattern = WikiLinks(self.WIKILINK_RE, self.getConfigs())
        wikilinkPattern.md = md
        md.inlinePatterns.add('wikilink', wikilinkPattern, "_begin")

class WikiLinks(Pattern):
    def __init__(self, pattern, config):
        super(WikiLinks, self).__init__(pattern)
        self.config = config

    def handleMatch(self, m):
        namespace_ = getattr(self.md, 'namespace_', '')

        wikilink = m.group('article_name')
        link_text = m.group('link_text')

        if wikilink.strip():
            base_url, end_url, html_class = self._getMeta()
            label = m.group(2).strip()
            url = self.config['build_url'](label, namespace_)
            a = etree.Element('a')

            if link_text:
                a.text = link_text
            else:
                a.text = label
            a.set('href', url)
            if html_class:
                a.set('class', html_class)
        else:
            a = ''
        return a

    def _getMeta(self):
        """ Return meta data or config data. """
        base_url = self.config['base_url']
        end_url = self.config['end_url']
        html_class = self.config['html_class']
        if hasattr(self.md, 'Meta'):
            if 'wiki_base_url' in self.md.Meta:
                base_url = self.md.Meta['wiki_base_url'][0]
            if 'wiki_end_url' in self.md.Meta:
                end_url = self.md.Meta['wiki_end_url'][0]
            if 'wiki_html_class' in self.md.Meta:
                html_class = self.md.Meta['wiki_html_class'][0]
        return base_url, end_url, html_class

def makeExtension(*args, **kwargs):
    return ThorsonWikiLinkExtension(*args, **kwargs)
