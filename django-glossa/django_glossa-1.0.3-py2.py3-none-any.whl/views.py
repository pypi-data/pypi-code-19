# -*- coding: utf-8 -*-
from __future__ import absolute_import
import logging
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView

from . import models, settings
from .helpers import index_list

logger = logging.getLogger(__name__)


class GlossaryBaseView(object):
    model = models.Term

    def get_letter(self):
        return self.kwargs['current']

    def get_queryset(self):
        """Filtra in base alla lettera corrente"""
        queryset = super(GlossaryBaseView, self).get_queryset()
        initial = self.get_letter()
        if initial:
            queryset = queryset.filter(pk__istartswith=initial)
        return queryset.order_by('name')

    def get_title(self, context):
        return _("Glossario")

    def get_context_data(self, **kwargs):
        data = super(GlossaryBaseView, self).get_context_data(**kwargs)

        current = self.get_letter().upper()
        data.update(current=current, mainindex=index_list())
        data['page_title'] = self.get_title(data)
        if settings.TERMS_INDEX_COLUMNS and settings.TERMS_INDEX_COLUMNS > 1:
            items = self.get_queryset().count()
            if items:
                data['glossary_columns'] = settings.TERMS_INDEX_COLUMNS
                data['per_col'] = (items + settings.TERMS_INDEX_COLUMNS - 1) / settings.TERMS_INDEX_COLUMNS
        return data


class TermListView(GlossaryBaseView, ListView):
    def get_title(self, context):
        return _(u"Glossario: {current}").format(**context)


class TermDetailView(GlossaryBaseView, DetailView):
    def get_title(self, context):
        return _(u"Glossario: {term}").format(term=context['object'].name)

    def get_context_data(self, **kwargs):
        kwargs.setdefault('term_list', self.get_queryset())
        return super(TermDetailView, self).get_context_data(**kwargs)

    def render_to_response(self, context, **response_kwargs):
        term = context['object']
        if term.alias:
            seen = {term.pk}
            while term.alias:
                if term.alias.pk in seen:
                    logger.error("Glossary alias loop for {}".format(term))
                else:
                    seen.add(term.alias.pk)
                    term = term.alias
            return HttpResponseRedirect(term.get_url())
        return super(TermDetailView, self).render_to_response(context, **response_kwargs)
