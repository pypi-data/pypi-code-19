from django.apps import AppConfig
from django.conf.urls import url
from django.views.generic import TemplateView
from material.frontend import ModuleURLResolver
from material.frontend.apps import ModuleMixin, MaterialFrontendConfig
from django.utils.translation import ugettext_lazy as _


class MdmConfig(ModuleMixin, MaterialFrontendConfig):
    order = 1
    name = 'nmdm'
    # icon = '<i class="material-icons">database</i>'
    icon = '<i class="material-icons">dns</i>'
    verbose_name = _('Master data')

    # @property
    # def urls(self):
    #     index_view = TemplateView.as_view(template_name='npolling/index.html')
    #
    #     return ModuleURLResolver('^', [url('^$', index_view, name="index")], module=self, app_name='npolling', namespace='npolling')
    #
    # def index_url(self):
    #     return '/'
    #
    # def installed(self):
    #     return True
