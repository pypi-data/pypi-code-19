# coding: utf-8
from django.core.paginator import Paginator


def paginate_in_context(request, objects, context, objects_name_in_context, per_page=10):
    page = int(request.GET.get('page', '1'))
    notifications_paginator = Paginator(objects.all(), per_page)
    notifications_page = notifications_paginator.page(page)
    context[objects_name_in_context] = context["page_obj"] = notifications_page
    context["is_paginated"] = notifications_page.has_other_pages()
    context["paginator"] = notifications_paginator
