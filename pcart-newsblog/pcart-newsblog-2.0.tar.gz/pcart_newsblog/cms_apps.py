from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class NewsBlogApphook(CMSApp):
    app_name = "pcart_newsblog"
    name = _("News & Blog")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["pcart_newsblog.urls"]

apphook_pool.register(NewsBlogApphook)
