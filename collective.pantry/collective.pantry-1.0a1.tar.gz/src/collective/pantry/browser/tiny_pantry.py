# -*- coding: utf-8 -*-
from collective.pantry.interfaces import PANTRY_DIRECTORY
from plone import api
from plone.app.theming.interfaces import THEME_RESOURCE_NAME
from plone.app.theming.utils import getCurrentTheme
from plone.app.theming.utils import isThemeEnabled
from plone.resource.utils import queryResourceDirectory
from Products.Five.browser import BrowserView

import json


class TinyPantry(BrowserView):

    def __call__(self):
        pc = api.portal.get_tool('portal_catalog')
        brains = pc.searchResults(
            portal_type='Snippet',
            sort_on='getObjPositionInParent')

        user_pantry = []
        for brain in brains:
            user_pantry.append(dict(
                title=brain.Title,
                description=brain.Description,
                url='{0}/raw'.format(brain.getURL())
            ))

        theme_pantry = []
        if isThemeEnabled(self.request):
            currentTheme = getCurrentTheme()
            if currentTheme is not None:
                themeDirectory = queryResourceDirectory(
                    THEME_RESOURCE_NAME, currentTheme)
                if themeDirectory is not None:
                    if themeDirectory.isDirectory(PANTRY_DIRECTORY):
                        theme_pantry = self.get_theme_pantry(themeDirectory)

        if theme_pantry:
            pantry = user_pantry + theme_pantry
        else:
            pantry = user_pantry
        self.request.response.setHeader('Content-Type', 'application/json')
        return json.dumps(pantry, indent=2, sort_keys=True)

    def get_theme_pantry(self, themeDirectory):
        pantry_directory = themeDirectory[PANTRY_DIRECTORY]
        result = []
        for snippet in pantry_directory.listDirectory():
            if snippet.endswith('.html') and \
               pantry_directory.isFile(snippet):
                snippet_info = dict(
                    url='++{0}++{1}/{2}/{3}'.format(
                        THEME_RESOURCE_NAME,
                        themeDirectory.__name__,
                        PANTRY_DIRECTORY,
                        snippet),
                    title=snippet.strip('.html'),
                    description=''
                )
                result.append(snippet_info)

        return result
