from plone.app.layout.viewlets.common import ViewletBase
from plone.memoize.instance import memoize



class Tablebehavior(ViewletBase):
    """nothing here yet"""

    @property
    def construct(self):
        """returns the urls that will embed the map """
        
        return """
        %(something)s
        """  % {
        'somethihng' : self.context.table,
        }