from django.http import HttpResponse


def empty(request):

    return HttpResponse("" + request.META["PATH_INFO"], content_type="text/plain")
