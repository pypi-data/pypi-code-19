# -*- coding: utf-8 -*-
"""Tile implementation."""

# python imports
from pygments import (
    formatters,
    highlight,
    lexers,
)
from pygments.util import ClassNotFound
import cgi
import requests

# zope imports
from plone import tiles
from plone.app.standardtiles import _PMF
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.supermodel.model import Schema
from plone.tiles.directives import ignore_querystring
from zope import schema
from zope.component import queryUtility

# local imports
from collective.tiles.githubgist import _


class IGithubGistTile(Schema):
    """A tile that shows Gists from GitHub."""

    tile_title = schema.TextLine(
        description=_PMF(
            u'The title will also be used to create identifying class on '
            u'that tile'
        ),
        required=True,
        title=_PMF(u'Title'),
    )

    show_title = schema.Bool(
        default=True,
        title=_PMF(u'Show tile title'),
    )

    title_level = schema.Choice(
        default=u'h2',
        required=False,
        title=_(u'Headline level'),
        values=(u'h1', u'h2', u'h3', u'h4', u'h5', u'h6'),
    )

    ignore_querystring('html_snippet')
    gist_url = schema.TextLine(
        title=_(u'Github Gist URL'),
        required=True,
    )

    gist_file_name = schema.TextLine(
        description=_(
            u'If specified only the given filename of a multi file gist '
            u'will be shown.'
        ),
        required=False,
        title=_(u'Filename'),
    )

    use_pygments = schema.Bool(
        default=False,
        description=_(
            u'If enabled, Pygments Syntax Highlighter will be used and the '
            u'gist will be rendered in HTML. Otherwise, the JS embedding '
            u'is used.'
        ),
        required=False,
        title=_(u'Use Pygments Syntax Highlighter')
    )

    pygments_language = schema.TextLine(
        description=_(
            u'Specify the language (lexer) which should be used for syntax '
            u'highlighting. If no language is given we try to get it from the '
            u'file name. This option has no effect if pygments is disabled.'
        ),
        required=False,
        title=_(u'Pygments Language'),
    )

    pygments_style = schema.TextLine(
        description=_(
            u'Specify the style which should be used for syntax '
            u'highlighting. If no style is given we set it to '
            u'"colorful". This option has no effect if pygments is disabled.'
        ),
        required=False,
        title=_(u'Pygments Style'),
    )

    pygments_inline_css = schema.Bool(
        default=False,
        description=_(
            u'If enabled, CSS definitions will be applied inline. If '
            u'disabled, please make sure you have some CSS definitions for '
            u'the highlighting in your theme.'
        ),
        required=False,
        title=_(u'Pygments Inline Styles'),
    )

    pygments_linenos = schema.Bool(
        default=False,
        description=_(
            u'If enabled, line number are shown.'
        ),
        required=False,
        title=_(u'Pygments Line Numbers'),
    )


class GithubGistTile(tiles.Tile):
    """A tile that shows Gists from GitHub."""

    @property
    def tile_id(self):
        return queryUtility(IIDNormalizer).normalize(
            self.data.get('tile_title')
        )

    @property
    def tile_title(self):
        return self.data.get('tile_title')

    @property
    def show_title(self):
        return self.data.get('show_title')

    @property
    def title_level(self):
        return self.data.get('title_level') or u'h2'

    @property
    def gist_url(self):
        url = u'{0}.js'.format(self.data.get('gist_url'))
        if self.gist_file_name is not None:
            url += '?file={0}'.format(self.gist_file_name)
        return url

    @property
    def gist_file_name(self):
        return self.data.get('gist_file_name')

    @property
    def use_pygments(self):
        return self.data.get('use_pygments') or False

    def pygments_lexer(self):
        language = self.data.get('pygments_language')
        lexer = None
        if language is not None:
            try:
                lexer = lexers.get_lexer_by_name(language)
            except ClassNotFound:
                lexer = None

        if lexer is None and self.gist_file_name is not None:
            try:
                lexer = lexers.find_lexer_class_for_filename(
                    self.gist_file_name,
                )
            except ClassNotFound:
                lexer = None
            else:
                lexer = lexer()

        if lexer is None:
            lexer = lexers.TextLexer()

        return lexer

    def gist_raw_url(self, gist_id):
        url = 'https://gist.githubusercontent.com/raw/{0}'.format(gist_id)
        if self.gist_file_name is not None:
            url += '/{0}'.format(self.gist_file_name)
        return url

    @property
    def gist_id(self):
        try:
            gist_id = self.data.get('gist_url').rsplit('/')[-1]
        except AttributeError:
            gist_id = None
        return gist_id

    def fetch_gist(self):
        """Fetch a gist and return the contents as a string."""
        url = self.gist_raw_url(self.gist_id)
        response = requests.get(url)

        if response.status_code != 200:
            return u''
        body = response.text
        if not body:
            return u''

        return body

    def render_code(self):
        """Render a piece of code into HTML."""
        code = self.fetch_gist()
        return '<pre><code>{0}</code></pre>'.format(cgi.escape(code))

    def render_pygments_code(self):
        """Render a piece of code into HTML."""
        code = self.fetch_gist()
        lexer = self.pygments_lexer()
        formatter = formatters.HtmlFormatter(
            linenos=(self.data.get('pygments_linenos') and 'table') or False,
            noclasses=self.data.get('pygments_inline_css') or False,
            style=self.data.get('pygments_style') or 'colorful',
        )
        return highlight(code, lexer, formatter)
