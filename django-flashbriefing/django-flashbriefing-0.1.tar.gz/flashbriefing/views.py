from django.http import JsonResponse, HttpResponseNotFound
from django.views.generic import DetailView

from .feeds import jsonfeed
from .models import Feed


class FeedView(DetailView):
    model = Feed
    allowed_formats = ('json',)
    slug_field = 'uuid'
    slug_url_kwarg = 'uuid'

    def get(self, request, *args, **kwargs):
        self.format = kwargs.get('format')
        if self.format not in self.allowed_formats:
            return HttpResponseNotFound()
        return super(FeedView, self).get(request, *args, **kwargs)

    def render_to_response(self, context, **response_kwargs):
        if self.format == 'json':
            return self.render_to_json()
        elif self.format == 'rss':
            return self.render_to_rss()
        return HttpResponseNotFound()

    def render_to_json(self):
        # data = jsonfeed(self.object.published_items())
        data = jsonfeed(self.object.items.all()[:5])
        if len(data) == 1:
            data = data[0]
        return JsonResponse(data, safe=False)

    def render_to_rss(self):
        pass
