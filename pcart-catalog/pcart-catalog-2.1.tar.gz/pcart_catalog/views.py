# from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.http import Http404, QueryDict, HttpResponseNotFound, JsonResponse
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render
from django.contrib.sites.shortcuts import get_current_site
from django.views.decorators.csrf import csrf_exempt
from django.core.cache import cache
# from django.conf import settings
from . import settings as pcart_settings
from .models import (
    Collection,
    Product,
    ProductVariant,
)
from .utils import (
    split_collection_slug,
    filter_slug_to_tags,
    normalize_filter_tags,
)
# from .signals import product_page_visit


AVAILABLE_COLLECTION_PARAMS = ['page', 'sort', 'view', 'json']
COLLECTION_CACHE_TIMEOUT = 60 * 15


@require_http_methods(['GET'])
def collection_view(request, slug, view='default'):
    from .filtering import ProductsFilterManager

    is_ajax = request.is_ajax()

    _params = QueryDict(mutable=True)
    for k, v in request.GET.items():
        if k in AVAILABLE_COLLECTION_PARAMS:
            _params.update({k: v})

    json_response = request.GET.get('json', False) == 'true'

    cache_key = '%s?%s%s' % (
        request.path_info,
        _params.urlencode(),
        '|ajax' if is_ajax else '')
    result = cache.get(cache_key)
    if result and not json_response:
        return result

    collection_slug, filter_chunks = split_collection_slug(slug)
    try:
        collection = Collection.objects.get(slug=collection_slug, site_id=get_current_site(request).id)
    except Collection.DoesNotExist:
        response = HttpResponseNotFound('collection not found')
        cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response

    filter_tags, vendors, prices, normalized_url_chunks, _redirect = filter_slug_to_tags(collection, filter_chunks)
    if _redirect:
        redirect_url = collection.get_absolute_url() + '/'.join(normalized_url_chunks) + '/'
        response = redirect(redirect_url)
        cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response

    ordering_type = request.GET.get('sort', pcart_settings.PCART_COLLECTION_DEFAULT_ORDERING)
    collection_view = request.GET.get('view', view)
    page = request.GET.get('page', 1)

    filter_manager = ProductsFilterManager(collection=collection, view=collection_view, sort=ordering_type)
    filter_manager.set_page(page)
    filter_manager.set_filters(filter_tags=filter_tags, vendors=vendors, prices=prices)

    context = filter_manager.get_context()
    context.update({
        'is_ajax': is_ajax,
        'page_url': request.path,
    })
    if json_response:
        context['collection'] = collection.as_dict()
        context['products'] = list(map(lambda x: x.as_dict(), context['products']))
        response = JsonResponse(context, safe=True)
        return response
    else:
        response = render(request, context['template_name'], context)
        cache.set(cache_key, response, COLLECTION_CACHE_TIMEOUT)
        return response



@csrf_exempt
@require_http_methods(['POST'])
def filter_form_dispatcher(request, collection_slug):
    vendors = request.POST.getlist('vendor')
    filter_tags = request.POST.getlist('tag')

    price = request.POST.get('price')
    if price is not None:
        price_from, price_to = price.split(request.POST.get('price-delimiter', ','))
    else:
        price_from = request.POST.get('price-from')
        price_to = request.POST.get('price-to')

    try:
        price_from = float(price_from)
    except ValueError:
        price_from = None
    try:
        price_to = float(price_to)
    except ValueError:
        price_to = None
    prices = (price_from, price_to)

    collection = Collection.objects.get(slug=collection_slug)
    _url = collection.get_absolute_url() + '/'.join(
        normalize_filter_tags(
            collection,
            vendors,
            prices,
            filter_tags,
        )) + '/'
    return redirect(_url)


def redirect_to_collections(request):
    return redirect('pcart_collection:all-collections')


class ProductDetailView(DetailView):
    model = Product
    context_object_name = 'product'
    template_name = 'catalog/product.html'

    def get_context_data(self, **kwargs):
        context = super(ProductDetailView, self).get_context_data(**kwargs)

        object_id = self.get_object().id
        setattr(self.request, 'productid', object_id)

        return context

    def get_object(self, queryset=None):
        try:
            if queryset is None:
                queryset = self.model.objects.filter(published=True)
            return queryset.get(slug=self.kwargs['product_slug'])
        except Product.DoesNotExist:
            raise Http404


class ProductVariantDetailView(DetailView):
    model = ProductVariant
    context_object_name = 'variant'
    template_name = 'catalog/variant.html'

    def get_context_data(self, **kwargs):
        context = super(ProductVariantDetailView, self).get_context_data(**kwargs)

        object = self.get_object()
        object_id = object.id

        setattr(self.request, 'productid', object_id)

        return context

    def get_object(self, queryset=None):
        try:
            if queryset is None:
                queryset = self.model.objects.filter(product__published=True)
            return queryset.get(slug=self.kwargs['variant_slug'], product__slug=self.kwargs['product_slug'])
        except Product.DoesNotExist:
            raise Http404


def collections_list_view(request, template_name='catalog/collections.html'):
    collections = Collection.objects.filter(published=True)
    context = {
        'collections': collections,
        'page_url': request.path,
    }
    return render(request, template_name, context)
