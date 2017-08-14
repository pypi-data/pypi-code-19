from django.utils.translation import ugettext as _
from cms.plugin_base import CMSPluginBase
from cms.plugin_pool import plugin_pool
from .models import CollectionPluginModel
from .forms import CollectionPluginForm


class CollectionPluginPublisher(CMSPluginBase):
    model = CollectionPluginModel  # model where plugin data are saved
    form = CollectionPluginForm
    module = _("Catalog")
    name = _("Collection")  # name of the plugin in the interface
    render_template = "catalog/plugins/collection_plugin.html"

    def render(self, context, instance, placeholder):
        from .filtering import ProductsFilterManager
        from .utils import filter_slug_to_tags

        filter_manager = ProductsFilterManager(
            collection=instance.collection,
            view=instance.template_name,
            sort=instance.sorting)
        filter_chunks = instance.filter_string.split('/')
        filter_tags, vendors, prices, normalized_url_chunks, _redirect = filter_slug_to_tags(
            instance.collection, filter_chunks)
        filter_manager.set_filters(filter_tags=filter_tags, vendors=vendors, prices=prices)
        context = filter_manager.get_context()
        context.update({'instance': instance})
        return context

plugin_pool.register_plugin(CollectionPluginPublisher)
