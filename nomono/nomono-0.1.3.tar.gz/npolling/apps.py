from django.apps import AppConfig
from material.frontend.apps import ModuleMixin, MaterialFrontendConfig
from django.utils.translation import ugettext_lazy as _


class PollingConfig(ModuleMixin, MaterialFrontendConfig):
    order = 1
    name = 'npolling'
    # icon = '<i class="material-icons">database</i>'
    icon = '<i class="material-icons">dns</i>'
    verbose_name = _('Reports')