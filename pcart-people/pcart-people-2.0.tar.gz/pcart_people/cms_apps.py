from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _


class PeopleApphook(CMSApp):
    app_name = "pcart_people"
    name = _("People")

    def get_urls(self, page=None, language=None, **kwargs):
        return ["pcart_people.urls"]

apphook_pool.register(PeopleApphook)
