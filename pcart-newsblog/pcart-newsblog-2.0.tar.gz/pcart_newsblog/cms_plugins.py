from django.utils.translation import ugettext as _
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import ArticleBlockPluginModel
from .forms import ArticleBlockPluginForm


class ArticleBlockPluginPublisher(CMSPluginBase):
    model = ArticleBlockPluginModel  # model where plugin data are saved
    form = ArticleBlockPluginForm
    module = _("News & Blog")
    name = _("Article block")  # name of the plugin in the interface
    render_template = "newsblog/plugins/article_block.html"

    def render(self, context, instance, placeholder):
        context.update({'instance': instance})
        return context

plugin_pool.register_plugin(ArticleBlockPluginPublisher)
