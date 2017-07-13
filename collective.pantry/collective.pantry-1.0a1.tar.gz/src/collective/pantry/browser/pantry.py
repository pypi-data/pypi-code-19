# -*- coding: utf-8 -*-
from collective.pantry.interfaces import PANTRY_DIRECTORY
from plone import api
from plone.app.theming.interfaces import THEME_RESOURCE_NAME
from plone.app.theming.utils import getCurrentTheme
from plone.app.theming.utils import isThemeEnabled
from plone.resource.utils import queryResourceDirectory
from plone.subrequest import subrequest
from Products.CMFPlone.resources import add_resource_on_request
from Products.Five.browser import BrowserView


class Pantry(BrowserView):

    def __init__(self, context, request):
        super(Pantry, self).__init__(context, request)
        add_resource_on_request(self.request, 'prismjs')
        add_resource_on_request(self.request, 'mockup-patterns-toggle')

    def just_snippet(self, snippet):
        """ bs4 returns a formal HTML document on prettyfy. We only want the
        snippet """
        snippet = snippet.replace('  </body>\n</html>\n', '')
        return snippet.replace('<html>\n  <head>\n  </head>\n  <body>\n', '')

    def get_snippet_html(self, url):
        return subrequest(url).getBody()

    def get_user_pantry(self):
        pc = api.portal.get_tool('portal_catalog')
        brains = pc.searchResults(
            portal_type='Snippet',
            sort_on='getObjPositionInParent')

        user_pantry = []
        for brain in brains:
            user_pantry.append(dict(
                title=brain.Title,
                description=brain.Description,
                url='{}/raw'.format(brain.getURL())
            ))

        return user_pantry

    def get_theme_pantry(self):
        theme_pantry = []
        if isThemeEnabled(self.request):
            currentTheme = getCurrentTheme()
            if currentTheme is not None:
                themeDirectory = queryResourceDirectory(
                    THEME_RESOURCE_NAME, currentTheme)
                if themeDirectory is not None:
                    if themeDirectory.isDirectory(PANTRY_DIRECTORY):
                        theme_pantry = self.get_theme_pantry_info(
                            themeDirectory)

        return theme_pantry

    def get_theme_pantry_info(self, themeDirectory):
        pantry_directory = themeDirectory[PANTRY_DIRECTORY]
        result = []
        for snippet in pantry_directory.listDirectory():
            if snippet.endswith('.html') and \
               pantry_directory.isFile(snippet):
                snippet_info = dict(
                    url='++{}++{}/{}/{}'.format(
                        THEME_RESOURCE_NAME,
                        themeDirectory.__name__,
                        PANTRY_DIRECTORY,
                        snippet),
                    title=snippet.strip('.html'),
                    description=''
                )
                result.append(snippet_info)

        return result
