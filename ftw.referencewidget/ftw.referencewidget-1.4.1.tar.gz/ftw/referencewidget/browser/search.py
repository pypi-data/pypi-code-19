from ftw.referencewidget.browser.utils import extend_with_batching
from ftw.referencewidget.browser.utils import get_root_path_from_source
from ftw.referencewidget.browser.utils import get_selectable_types
from ftw.referencewidget.browser.utils import get_sort_options
from ftw.referencewidget.browser.utils import get_sort_order_options
from ftw.referencewidget.browser.utils import get_traversal_types
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
import json


class SearchView(BrowserView):

    def __call__(self):

        json_prep = {'items': [],
                     'sortOnOptions': get_sort_options(self.request),
                     'sortOrderOptions': get_sort_order_options(self.request)}

        search_term = self.request.get('term')
        if not search_term:
            return json.dumps(json_prep)

        if not search_term.endswith("*"):
            search_term += "*"
        search_types = get_selectable_types(self.context)

        query = {'portal_type': search_types,
                 'Title': search_term,
                 'sort_order': self.request.get('sort_order',
                                                u'ascending').encode('utf-8'),
                 'sort_on': self.request.get('sort_on',
                                             u'modified').encode('utf-8')}

        query.update(self.context.traversal_query)

        root_path = get_root_path_from_source(self.context)
        if root_path:
            query['path'] = root_path

        catalog = getToolByName(self.context.context, 'portal_catalog')
        results = catalog(query)
        results, batch_html = extend_with_batching(self.context, results)

        json_prep['batching'] = batch_html

        traversel_type = get_traversal_types(self.context)

        for item in results:
            contenttype = 'contenttype-' \
                + item.portal_type.replace('.', '-').lower()

            traversable = item.is_folderish and  \
                (item.portal_type in traversel_type)

            label = '{0} ({1})'.format(item.Title, item.getPath())
            json_prep['items'].append({'title': label,
                                       'path': item.getPath(),
                                       'selectable': True,
                                       'content-type': contenttype,
                                       'traversable': traversable
                                       })

        self.request.RESPONSE.setHeader("Content-type", "application/json")
        return json.dumps(json_prep)
