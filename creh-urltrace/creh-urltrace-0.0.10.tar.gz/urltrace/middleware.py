from urltrace.actions import register
import urlparse

class UrlTraceMiddleware():

    def process_request(self, request):
        origin = ""
        if request.GET.get("utm_source"):
            origin = request.GET.get("utm_source")
        else:
            if "HTTP_HOST" in request.META:
                url_host = request.META['HTTP_HOST']
                if 'HTTP_REFERER' in request.META:
                    if url_host in request.META['HTTP_REFERER']:
                        origin = request.META['HTTP_REFERER'].split(url_host)[1]
                    else:
                        origin = request.META['HTTP_REFERER']

        if origin <> "" and origin[0] <> "/":
            netloc = urlparse.urlparse(origin).netloc
            if netloc <> "":
                origin = netloc
            # register the origin and asign group
            register.register_url_trace(origin)

            try:
                request.session["name_group_trace"] = origin
            except AttributeError:
                request.session = {"name_group_trace" : origin}

        pass
