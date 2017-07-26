# -*- coding: utf-8 -*-
from urltrace.models import UrlTrace,UrlTraceGroup
from urltrace import constants

def register_url_trace(url_trace):
    #validate url exist in cache
    list_url_trace = UrlTrace.objects.filter(url_trace=url_trace)

    if len(list_url_trace)<=0:
        # update views in database
        url_trace_group_default = UrlTraceGroup.objects.get(id=constants.DEFAULT_REGISTER)
        objUrlTrace = UrlTrace(url_trace=url_trace, url_trace_group=url_trace_group_default)
        objUrlTrace.save()
        name_group_trace = url_trace_group_default.group_name
    else:
        name_group_trace = list_url_trace[0].url_trace_group.group_name

    return name_group_trace