from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.views.generic.base import TemplateView

from .activecollab import get_activecollab, post_activecollab


class IndexPageView(LoginRequiredMixin, TemplateView):
    template_name = 'activecollab_digger/index.html'


def tasks(request):
    if request.method == 'POST':
        return _post_task(request)

    return _get_tasks(request)


def _get_tasks(request):
    r = get_activecollab('projects/{}/tasks'.format(settings.AC_PROJECT_ID))

    if r.status_code != 200:
        return JsonResponse({'error': r.status_code,
                             'message': r.json()['message']})

    return JsonResponse(r.json())


def _post_task(request):
    params = {
        'name': request.POST.get('name'),
        'body': request.POST.get('body'),
        'created_by_id': settings.AC_USER
    }

    r = post_activecollab('projects/{}/tasks'.format(settings.AC_PROJECT_ID),
                          params=params)

    if r.status_code != 200:
        return JsonResponse({'error': r.status_code,
                             'message': r.json()['message']})

    return JsonResponse(r.json())
