from datetime import date
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from zope.component import getMultiAdapter


class BelowViewlet(ViewletBase):
    index = ViewPageTemplateFile('belowportlets.pt')

    def update(self):
        super(BelowViewlet, self).update()
        self.year = date.today().year

    def render_below_portlets(self):
        """

        """
        portlet_manager = getMultiAdapter(
            (self.context, self.request, self.__parent__), name='medialog.belowportlets')
        portlet_manager.update()
        return portlet_manager.render()
        
        
class AboveViewlet(ViewletBase):
    index = ViewPageTemplateFile('aboveportlets.pt')

    def update(self):
        super(AboveViewlet, self).update()
        self.year = date.today().year

    def render_above_portlets(self):
        """

        """
        portlet_manager = getMultiAdapter(
            (self.context, self.request, self.__parent__), name='medialog.aboveportlets')
        portlet_manager.update()
        return portlet_manager.render()