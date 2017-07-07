# -*- coding: utf-8 -*-
from __future__ import absolute_import
from django.contrib.admin import site as admin_site
from django.contrib.admin.views.main import ChangeList
from django.contrib.messages import warning
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _

from .helpers import list2excel
from .settings import MAX_ONLINE_EXPORT_RECORDS, GLOBAL_ACTIONS


def export(modeladmin, request, queryset, force_text=False):
    """Azione massiva di esportazione in Excel"""
    model = modeladmin.model
    if not modeladmin.has_change_permission(request):
        raise PermissionDenied
    if queryset is None:
        cl = ChangeList(
            request, model,
            modeladmin.list_display,
            modeladmin.list_display_links,
            modeladmin.list_filter,
            modeladmin.date_hierarchy,
            modeladmin.search_fields,
            modeladmin.list_select_related,
            modeladmin.list_per_page,
            modeladmin.list_max_show_all,
            modeladmin.list_editable,
            modeladmin)
        get_queryset = (cl.get_query_set
                if hasattr(cl, 'get_query_set')
                else cl.get_queryset)
        queryset = get_queryset(request)
    cnt = queryset.count()
    max_num = getattr(model, '_export_max_items', MAX_ONLINE_EXPORT_RECORDS)
    if cnt > max_num:
        warning(request,
                u"L'esportazione di {0:d} righe sarebbe troppo onerosa. Prova a filtrare ulteriormente l'elenco in modo da "
                u"scendere sotto le {1:d}. Grazie.".format(cnt, max_num))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
    return list2excel(
        model, queryset=queryset, force_text=force_text).as_http_response()
export.short_description = _("Esporta XLS")


def mail_merge_export(modeladmin, request, queryset):
    """Azione massiva di esportazione per mail merge"""
    return export(modeladmin, request, queryset=queryset, force_text=True)
mail_merge_export.short_description = _("Esporta XLS per mail merge")

if GLOBAL_ACTIONS:
    admin_site.add_action(export)
    admin_site.add_action(mail_merge_export)
