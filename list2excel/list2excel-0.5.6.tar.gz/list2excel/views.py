# -*- coding: utf-8 -*-
from __future__ import absolute_import

from django.contrib.admin.sites import site
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.admin.views.main import ChangeList
from django.contrib.messages import warning
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from .helpers import list2excel
from .settings import MAX_ONLINE_EXPORT_RECORDS

try:
    from django.apps import apps

    get_model = apps.get_model
except ImportError:
    # Django<=1.7
    from django.db.models.loading import get_model


@staff_member_required
def export(request, app_label, model_name, queryset=None, force_text=False):
    """
    # Uso normale: mettere in admin/base_site.html
        {% if cl %}
            &nbsp;&nbsp;<a href="{% url 'list2excel' cl.opts.app_label cl.opts.object_name|lower %}{%if request.GET%}?{{request.GET.urlencode}
            Export <img src="{{ STATIC_URL }}images/excel.png" height="20px"></a>
        {% endif %}
    """
    model = get_model(app_label, model_name)
    model_admin = site._registry[model]
    if not model_admin.has_change_permission(request):
        raise PermissionDenied
    if queryset is None:
        cl = ChangeList(
            request, model,
            model_admin.list_display,
            model_admin.list_display_links,
            model_admin.list_filter,
            model_admin.date_hierarchy,
            model_admin.search_fields,
            model_admin.list_select_related,
            model_admin.list_per_page,
            model_admin.list_max_show_all,
            model_admin.list_editable,
            model_admin)
        get_queryset = (cl.get_query_set if hasattr(cl, 'get_query_set') else cl.get_queryset)
        queryset = get_queryset(request)
    cnt = queryset.count()
    max_num = getattr(model, '_export_max_items', MAX_ONLINE_EXPORT_RECORDS)
    if cnt > max_num:
        warning(request, u"Spiacente, l'esportazione di {0:d} righe sarebbe troppo onerosa. Prova a filtrare "
                         u"ulteriormente l'elenco in modo da scendere sotto le {1:d}. Grazie.".format(cnt, max_num))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return list2excel(model, queryset=queryset, force_text=force_text).as_http_response()
